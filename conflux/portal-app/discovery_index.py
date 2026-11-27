"""Opt-in local project discovery, independent of Portal HTTP and storage.

Indexes names and stat metadata only. No file contents, network, execution,
background watcher, or project writes. Linux/Python 3.10+.
"""
import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import shutil
import subprocess
import stat
import sys
import time

MAX_ENTRIES = 20000
MAX_DEPTH = 24
MAX_RESULTS = 200
SCHEMA_VERSION = 3
SKIP_DIRS = {"node_modules", "__pycache__"}
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


class DiscoveryError(Exception):
    pass


def default_db():
    state = os.environ.get("XDG_STATE_HOME")
    base = Path(state) if state and Path(state).is_absolute() else Path.home() / ".local/state"
    return base / "conflux-portal" / "discovery" / "index.sqlite3"


def project_name(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 100:
        raise DiscoveryError("Use a project name of 1–100 characters.")
    return value.strip()


def selected_root(value, db):
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise DiscoveryError("Choose an explicit absolute project directory.")
    root = path.resolve(strict=True)
    home = Path.home().resolve()
    storage = Path(db).expanduser().resolve().parent
    if (not root.is_dir() or root == Path(root.anchor) or root == home
            or root in home.parents or root == storage
            or root in storage.parents or storage in root.parents):
        raise DiscoveryError("Choose a specific project folder, not a home, system or index-storage root.")
    return root


def collect(root, *, max_entries=MAX_ENTRIES, max_depth=MAX_DEPTH):
    """Read bounded metadata via directory descriptors, not symlink targets."""
    files = []
    directories = [""]  # root marker; includes empty traversed directories
    visited = 0
    skipped = 0
    with closing_fd(os.open(root, DIR_FLAGS)) as fd:
        device = os.fstat(fd).st_dev

        def walk(dir_fd, relative, depth):
            nonlocal visited, skipped
            with os.scandir(dir_fd) as entries:
                for entry in entries:
                    visited += 1
                    if visited > max_entries:
                        raise DiscoveryError("Scan entry limit reached; choose a smaller project folder.")
                    name = entry.name
                    if name.startswith("."):
                        skipped += 1
                        continue
                    try:
                        name.encode("utf-8")
                    except UnicodeError:
                        skipped += 1
                        continue
                    info = entry.stat(follow_symlinks=False)
                    path = relative / name
                    if info.st_dev != device:
                        skipped += 1
                    elif stat.S_ISDIR(info.st_mode):
                        if name in SKIP_DIRS:
                            skipped += 1
                            continue
                        if depth >= max_depth:
                            raise DiscoveryError("Scan depth limit reached; choose a smaller project folder.")
                        with closing_fd(os.open(name, DIR_FLAGS, dir_fd=dir_fd)) as child:
                            actual = os.fstat(child)
                            if (actual.st_dev, actual.st_ino) != (info.st_dev, info.st_ino):
                                raise DiscoveryError("Folder changed during scan; retry.")
                            directories.append(path.as_posix())
                            walk(child, path, depth + 1)
                    elif stat.S_ISREG(info.st_mode):
                        files.append((path.as_posix(), info.st_size, info.st_mtime_ns))
                    else:
                        skipped += 1
        walk(fd, Path(), 0)
    return files, skipped, directories


class closing_fd:
    def __init__(self, fd):
        self.fd = fd

    def __enter__(self):
        return self.fd

    def __exit__(self, *_):
        os.close(self.fd)


def private_db(db):
    """Use a dedicated user-only directory and a regular private database."""
    db = Path(db).expanduser()
    if not db.is_absolute():
        raise DiscoveryError("Index path must be absolute.")
    db.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    parent = db.parent.lstat()
    if (not stat.S_ISDIR(parent.st_mode) or parent.st_uid != os.getuid()
            or parent.st_mode & 0o077):
        raise DiscoveryError("Index directory must be owned by you with mode 0700.")
    try:
        fd = os.open(db, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        info = db.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or info.st_mode & 0o077 or info.st_nlink != 1):
            raise DiscoveryError("Index must be a private regular file owned by you.")
    else:
        os.close(fd)
    return db


def connect(db):
    conn = sqlite3.connect(private_db(db), timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if version == 0:
                existing = conn.execute(
                    "SELECT name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'").fetchone()
                if existing:
                    raise DiscoveryError("Not an empty discovery database; no migration attempted.")
                conn.execute("CREATE TABLE projects (name TEXT PRIMARY KEY, root TEXT NOT NULL UNIQUE, scanned_ns INTEGER NOT NULL, skipped INTEGER NOT NULL)")
                conn.execute("CREATE TABLE files (project TEXT NOT NULL REFERENCES projects(name) ON DELETE CASCADE, path TEXT NOT NULL, bytes INTEGER NOT NULL, modified_ns INTEGER NOT NULL, PRIMARY KEY(project, path))")
                conn.execute("CREATE INDEX files_recent ON files(modified_ns DESC)")
            if version in (0, 1):
                # Additive migration: preserve all existing project/file rows.
                # No directory records for v1 snapshots until refreshed.
                conn.execute("CREATE TABLE directories (project TEXT NOT NULL REFERENCES projects(name) ON DELETE CASCADE, path TEXT NOT NULL, PRIMARY KEY(project, path))")
            if version in (0, 1, 2):
                conn.execute("CREATE TABLE discovery_preferences (id INTEGER PRIMARY KEY CHECK(id=1), launch_refresh INTEGER NOT NULL CHECK(launch_refresh IN (0,1)))")
                conn.execute("CREATE TABLE project_apps (project TEXT PRIMARY KEY REFERENCES projects(name) ON DELETE CASCADE, app TEXT NOT NULL, directory TEXT NOT NULL)")
                conn.execute("PRAGMA user_version = 3")
            elif version != SCHEMA_VERSION:
                raise DiscoveryError("Unsupported discovery index schema; no migration attempted.")
        return conn
    except BaseException:
        conn.close()
        raise


def scan(db, name, folder, *, max_entries=MAX_ENTRIES, max_depth=MAX_DEPTH):
    """Replace a project's snapshot only after a complete successful scan."""
    name = project_name(name)
    root = selected_root(folder, db)
    files, skipped, directories = collect(root, max_entries=max_entries, max_depth=max_depth)
    now = time.time_ns()
    with closing(connect(db)) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        previous = conn.execute("SELECT root FROM projects WHERE name = ?", (name,)).fetchone()
        if previous and previous["root"] != str(root):
            raise DiscoveryError("Project name already points elsewhere. Remove its index explicitly first.")
        other = conn.execute("SELECT name FROM projects WHERE root = ? AND name != ?", (str(root), name)).fetchone()
        if other:
            raise DiscoveryError("This folder is already registered under another project.")
        conn.execute("INSERT INTO projects VALUES (?, ?, ?, ?) ON CONFLICT(name) DO UPDATE SET scanned_ns=excluded.scanned_ns, skipped=excluded.skipped",
                     (name, str(root), now, skipped))
        conn.execute("DELETE FROM files WHERE project = ?", (name,))
        conn.executemany("INSERT INTO files VALUES (?, ?, ?, ?)",
                         ((name, *row) for row in files))
        conn.execute("DELETE FROM directories WHERE project = ?", (name,))
        conn.executemany("INSERT INTO directories VALUES (?, ?)", ((name, path) for path in directories))
    return {"project": name, "root": str(root), "indexed": len(files),
            "skipped": skipped, "scanned_ns": now}


def topology(conn, name):
    """Tree of traversed directories, or inferred parents for old snapshots."""
    paths = {row["path"] for row in conn.execute(
        "SELECT path FROM directories WHERE project=?", (name,))}
    complete = "" in paths
    if not complete:
        paths = {""}
        for row in conn.execute("SELECT path FROM files WHERE project=?", (name,)):
            parts = row["path"].split("/")[:-1]
            paths.update("/".join(parts[:i]) for i in range(1, len(parts)+1))
    children = {path: [] for path in paths}
    for path in paths - {""}:
        parent = path.rpartition("/")[0]
        children[parent].append(path)
    summaries = {}
    for path in sorted(paths, key=lambda p: (p.count("/") + bool(p)), reverse=True):
        branch = children[path]
        summaries[path] = {
            "path": path, "name": path.rpartition("/")[2],
            "children": len(branch),
            "folders": sum(1 + summaries[child]["folders"] for child in branch),
            "endpoints": sum(summaries[child]["endpoints"] for child in branch) if branch else 1,
            "depth": 1 + max(summaries[child]["depth"] for child in branch) if branch else 0,
        }
    return children, summaries, complete


def tree_slice(children, summaries, path, offset):
    if path not in children:
        raise DiscoveryError("Folder is not in the indexed snapshot.")
    paths = sorted(children[path], key=lambda p: (p.casefold(), p))
    return {"entries": [summaries[p] for p in paths[offset:offset+PAGE_SIZE]],
            "total": len(paths), "offset": offset}


def tree_page(db, project, directory="", offset=0):
    name = project_name(project)
    relative_parts(directory, allow_empty=True)
    if type(offset) is not int or not 0 <= offset <= 1000000:
        raise DiscoveryError("Invalid result offset.")
    with closing(connect(db)) as conn:
        conn.execute("BEGIN")
        if not conn.execute("SELECT 1 FROM projects WHERE name=?", (name,)).fetchone():
            raise DiscoveryError("Project is not registered.")
        children, summaries, complete = topology(conn, name)
        return {**tree_slice(children, summaries, directory, offset), "complete": complete}


def projects(db):
    with closing(connect(db)) as conn:
        conn.execute("BEGIN")
        rows = [dict(row) for row in conn.execute(
            "SELECT p.name, p.root, p.scanned_ns, p.skipped, COUNT(f.path) AS indexed "
            "FROM projects p LEFT JOIN files f ON p.name=f.project "
            "GROUP BY p.name ORDER BY p.name")]
        for row in rows:
            association = conn.execute("SELECT app, directory FROM project_apps WHERE project=?", (row["name"],)).fetchone()
            row["association"] = dict(association) if association else None
            children, summaries, complete = topology(conn, row["name"])
            row["topology"] = {**summaries[""], "complete": complete}
            row["tree"] = tree_slice(children, summaries, "", 0)
        return rows


def search(db, query="", project=None, limit=50, offset=0):
    if not isinstance(query, str) or len(query) > 500:
        raise DiscoveryError("Search text must be at most 500 characters.")
    if not isinstance(limit, int) or not 1 <= limit <= MAX_RESULTS:
        raise DiscoveryError("Result limit must be between 1 and 200.")
    if type(offset) is not int or not 0 <= offset <= 1000000:
        raise DiscoveryError("Invalid result offset.")
    # INSTR treats SQL wildcard characters literally; parameters are bound.
    statement = (
        "SELECT f.project, p.root, f.path, f.bytes, f.modified_ns, p.scanned_ns "
        "FROM files f JOIN projects p ON p.name=f.project "
        "WHERE (instr(lower(f.path), lower(?)) > 0 OR instr(lower(f.project), lower(?)) > 0)"
    )
    args = [query, query]
    if project is not None:
        statement += " AND f.project = ?"
        args.append(project_name(project))
    statement += " ORDER BY f.modified_ns DESC, f.project, f.path LIMIT ? OFFSET ?"
    args.extend((limit, offset))
    with closing(connect(db)) as conn:
        return [dict(row) for row in conn.execute(statement, args)]


PAGE_SIZE = 25
# Only familiar creative/document formats can be handed to a desktop
# association. Scripts, executables, shortcuts, HTML, archives and APKs
# are deliberately excluded. All other files can be located in their folder.
OPEN_SUFFIXES = frozenset({
    ".blend", ".fbx", ".obj", ".gltf", ".glb", ".stl", ".usd", ".usda",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".tga", ".exr",
    ".wav", ".flac", ".mp3", ".ogg", ".mp4", ".webm", ".mkv",
    ".txt", ".md", ".json", ".csv", ".pdf", ".odt", ".docx", ".xlsx",
    ".py", ".kt", ".java", ".cpp", ".h", ".cs", ".js", ".css", ".ini",
}) - {".py", ".js"}  # executable script formats remain reveal-only


def relative_parts(value, *, allow_empty=False):
    if not isinstance(value, str) or len(value) > 4096 or "\x00" in value:
        raise DiscoveryError("Invalid indexed path.")
    if not value and allow_empty:
        return []
    parts = value.split("/")
    if any(not p or p in (".", "..") or p.startswith(".") for p in parts):
        raise DiscoveryError("Choose an indexed relative path.")
    return parts


def folder_page(db, project, directory="", offset=0):
    name = project_name(project)
    relative_parts(directory, allow_empty=True)
    if type(offset) is not int or not 0 <= offset <= 1000000:
        raise DiscoveryError("Invalid result offset.")
    prefix = directory + "/" if directory else ""
    with closing(connect(db)) as conn:
        row = conn.execute("SELECT root, scanned_ns FROM projects WHERE name=?", (name,)).fetchone()
        if row is None:
            raise DiscoveryError("Project is not registered.")
        found = {}
        for file in conn.execute(
            "SELECT path, bytes, modified_ns FROM files WHERE project=? AND substr(path, 1, ?) = ?",
            (name, len(prefix), prefix)):
            tail = file["path"][len(prefix):]
            first, sep, _ = tail.partition("/")
            if sep:
                found[first] = {"name": first, "path": prefix + first, "kind": "folder"}
            else:
                found[first] = {**dict(file), "name": first, "kind": "file",
                                "project": name, "root": row["root"], "scanned_ns": row["scanned_ns"]}
        # Include actual traversed folders even when they contain no files.
        children, summaries, _ = topology(conn, name)
        if directory not in children:
            raise DiscoveryError("Folder is not in the indexed snapshot. Refresh the project.")
        for child in children[directory]:
            label = summaries[child]["name"]
            found[label] = {"name": label, "path": child, "kind": "folder"}
    entries = sorted(found.values(), key=lambda x: (x["kind"] != "folder", x["name"].casefold(), x["name"]))
    return {"entries": entries[offset:offset+PAGE_SIZE], "total": len(entries), "offset": offset}


def open_indexed(db, project, path, *, reveal=False):
    """Explicit desktop handoff of an indexed regular file, never a command."""
    name = project_name(project)
    parts = relative_parts(path)
    with closing(connect(db)) as conn:
        row = conn.execute(
            "SELECT p.root FROM files f JOIN projects p ON p.name=f.project WHERE f.project=? AND f.path=?",
            (name, path)).fetchone()
    if row is None:
        raise DiscoveryError("File is not in this project's index.")
    root = Path(row["root"])
    target = root.joinpath(*parts)
    # Revalidate every component and reject symlink replacement, missing
    # files, mount changes and executable mode. The desktop association
    # ultimately opens a pathname; do not use on actively modified/untrusted trees.
    if root.resolve(strict=True) != root:
        raise DiscoveryError("Project root changed. Refresh or register it again.")
    device = root.stat().st_dev
    current = root
    for i, part in enumerate(parts):
        current = current / part
        info = current.lstat()
        wanted = stat.S_ISREG if i == len(parts)-1 else stat.S_ISDIR
        if not wanted(info.st_mode) or info.st_dev != device:
            raise DiscoveryError("Indexed location changed. Refresh the project.")
    if not reveal and (target.suffix.lower() not in OPEN_SUFFIXES or info.st_mode & 0o111):
        raise DiscoveryError("This file type or executable is reveal-only.")
    opener = shutil.which("xdg-open")
    if not opener:
        raise DiscoveryError("Desktop opener (xdg-open) is unavailable.")
    subprocess.Popen([opener, str(target.parent if reveal else target)],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, start_new_session=True)
    return {"requested": True, "action": "reveal" if reveal else "open"}


APP_OPTIONS = {
    "pycharm": ("PyCharm", ("pycharm", "pycharm-community", "pycharm-professional"), ()),
    "studio": ("Android Studio", ("studio", "android-studio"), ()),
    "blender": ("Blender", ("blender",), ("org.blender.Blender",)),
    "code": ("Visual Studio Code", ("code",), ("com.visualstudio.code",)),
    "kate": ("Kate", ("kate",), ("org.kde.kate",)),
    "files": ("File manager", ("xdg-open",), ()),
}


def app_command(app):
    if not isinstance(app, str) or app not in APP_OPTIONS:
        raise DiscoveryError("Choose a supported application.")
    _, names, flatpaks = APP_OPTIONS[app]
    for name in names:
        path = shutil.which(name)
        if path:
            return [path]
    if app in ("pycharm", "studio"):
        scripts = Path.home() / ".local/share/JetBrains/Toolbox/scripts"
        for name in names:
            path = scripts / name
            if path.is_file() and os.access(path, os.X_OK):
                return [str(path)]
    flatpak = shutil.which("flatpak")
    if flatpak:
        for app_id in flatpaks:
            try:
                result = subprocess.run([flatpak, "info", app_id], stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL, timeout=3)
            except (OSError, subprocess.TimeoutExpired):
                continue
            if result.returncode == 0:
                return [flatpak, "run", app_id]
    return None


def app_options():
    # Detection is local; no network request, installation or app launch.
    return [{"id": app, "label": spec[0], "available": bool(app_command(app))}
            for app, spec in APP_OPTIONS.items()]


def preferences(db):
    if not os.path.lexists(db):
        return {"launch_refresh": False}
    with closing(connect(db)) as conn:
        row = conn.execute("SELECT launch_refresh FROM discovery_preferences WHERE id=1").fetchone()
        return {"launch_refresh": bool(row and row[0])}


def set_preferences(db, enabled):
    if type(enabled) is not bool:
        raise DiscoveryError("Choose whether launch refresh is enabled.")
    with closing(connect(db)) as conn, conn:
        conn.execute("INSERT INTO discovery_preferences VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET launch_refresh=excluded.launch_refresh", (int(enabled),))
    return {"launch_refresh": enabled}


def associate(db, project, app, directory=""):
    name = project_name(project)
    relative_parts(directory, allow_empty=True)
    if not isinstance(app, str) or (app and app not in APP_OPTIONS):
        raise DiscoveryError("Choose a supported application.")
    # Blender opens files, not projects. Keep it for file associations via
    # xdg-open; project shortcuts are directory-oriented.
    if app == "blender":
        raise DiscoveryError("Use Open on an indexed Blender file instead.")
    with closing(connect(db)) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        if not conn.execute("SELECT 1 FROM projects WHERE name=?", (name,)).fetchone():
            raise DiscoveryError("Project is not registered.")
        children, _, _ = topology(conn, name)
        if directory not in children:
            raise DiscoveryError("Choose an indexed project directory.")
        if app:
            conn.execute("INSERT INTO project_apps VALUES (?, ?, ?) ON CONFLICT(project) DO UPDATE SET app=excluded.app, directory=excluded.directory", (name, app, directory))
        else:
            conn.execute("DELETE FROM project_apps WHERE project=?", (name,))
    return {"associated": bool(app)}


def open_project(db, project):
    name = project_name(project)
    with closing(connect(db)) as conn:
        row = conn.execute("SELECT p.root, a.app, a.directory FROM projects p JOIN project_apps a ON p.name=a.project WHERE p.name=?", (name,)).fetchone()
        if not row:
            raise DiscoveryError("Choose a project application first.")
        children, _, _ = topology(conn, name)
        if row["directory"] not in children:
            raise DiscoveryError("Associated directory is no longer indexed.")
    root = Path(row["root"])
    parts = relative_parts(row["directory"], allow_empty=True)
    if root.resolve(strict=True) != root or not root.is_dir():
        raise DiscoveryError("Project root changed. Refresh the project.")
    device = root.stat().st_dev
    target = root
    for part in parts:
        target = target / part
        info = target.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_dev != device:
            raise DiscoveryError("Associated directory changed. Refresh the project.")
    command = app_command(row["app"])
    if not command:
        raise DiscoveryError("Application launcher is unavailable. Check your local installation.")
    subprocess.Popen([*command, str(target)], stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return {"requested": True, "app": row["app"]}


def forget(db, name):
    """Delete index records, never source files."""
    with closing(connect(db)) as conn, conn:
        count = conn.execute("DELETE FROM projects WHERE name = ?", (project_name(name),)).rowcount
    return {"removed_project_records": count}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=default_db(),
                        help="Private index path (normally leave unset)")
    sub = parser.add_subparsers(dest="command", required=True)
    scan_cmd = sub.add_parser("scan", help="Explicitly scan or refresh a project")
    scan_cmd.add_argument("--project", required=True)
    scan_cmd.add_argument("--root", required=True, type=Path)
    sub.add_parser("projects", help="List local project snapshots")
    find = sub.add_parser("search", help="Search indexed names, not file contents")
    find.add_argument("query", nargs="?", default="")
    find.add_argument("--project")
    find.add_argument("--limit", type=int, default=50)
    remove = sub.add_parser("forget", help="Remove a project from the index only")
    remove.add_argument("--project", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "scan":
            result = scan(args.db, args.project, args.root)
        elif args.command == "projects":
            result = projects(args.db)
        elif args.command == "search":
            result = search(args.db, args.query, args.project, args.limit)
        else:
            result = forget(args.db, args.project)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0
    except (DiscoveryError, OSError, ValueError, sqlite3.Error) as exc:
        print("Discovery: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
