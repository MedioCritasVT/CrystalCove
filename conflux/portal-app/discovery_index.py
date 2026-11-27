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
import stat
import sys
import time

MAX_ENTRIES = 20000
MAX_DEPTH = 24
MAX_RESULTS = 200
SCHEMA_VERSION = 1
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
                            walk(child, path, depth + 1)
                    elif stat.S_ISREG(info.st_mode):
                        files.append((path.as_posix(), info.st_size, info.st_mtime_ns))
                    else:
                        skipped += 1
        walk(fd, Path(), 0)
    return files, skipped


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
                conn.execute("PRAGMA user_version = 1")
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
    files, skipped = collect(root, max_entries=max_entries, max_depth=max_depth)
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
    return {"project": name, "root": str(root), "indexed": len(files),
            "skipped": skipped, "scanned_ns": now}


def projects(db):
    with closing(connect(db)) as conn:
        return [dict(row) for row in conn.execute(
            "SELECT p.name, p.root, p.scanned_ns, p.skipped, COUNT(f.path) AS indexed "
            "FROM projects p LEFT JOIN files f ON p.name=f.project "
            "GROUP BY p.name ORDER BY p.name")]


def search(db, query="", project=None, limit=50):
    if not isinstance(query, str) or len(query) > 500:
        raise DiscoveryError("Search text must be at most 500 characters.")
    if not isinstance(limit, int) or not 1 <= limit <= MAX_RESULTS:
        raise DiscoveryError("Result limit must be between 1 and 200.")
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
    statement += " ORDER BY f.modified_ns DESC, f.project, f.path LIMIT ?"
    args.append(limit)
    with closing(connect(db)) as conn:
        return [dict(row) for row in conn.execute(statement, args)]


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
