"""Disposable local fixtures; never scan the user's project or home."""
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

import discovery_index as discovery


class DiscoveryIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "work"
        self.root.mkdir()
        self.db = self.base / "private-index" / "index.sqlite3"

    def add(self, name, data=b"test"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def scan(self, **kw):
        return discovery.scan(self.db, "Demo", self.root, **kw)

    def test_search_refresh_and_forget_do_not_change_files(self):
        old = self.add("Models/tool.blend", b"original")
        new = self.add("Reports/notes.md")
        self.assertEqual(self.scan()["indexed"], 2)
        self.assertEqual(discovery.projects(self.db)[0]["indexed"], 2)
        self.assertEqual(discovery.search(self.db, "TOOL")[0]["path"], "Models/tool.blend")
        self.assertEqual(discovery.search(self.db, "Demo", project="Demo")[0]["project"], "Demo")
        self.assertEqual(discovery.search(self.db, "%"), [])
        self.assertEqual(discovery.search(self.db, "' OR 1=1 --"), [])
        old.unlink()
        self.add("Models/new.blend")
        self.assertEqual(self.scan()["indexed"], 2)
        self.assertFalse(discovery.search(self.db, "tool"))
        self.assertEqual(discovery.forget(self.db, "Demo")["removed_project_records"], 1)
        self.assertFalse(discovery.search(self.db))
        self.assertEqual(new.read_bytes(), b"test")
        self.assertTrue((self.root / "Models/new.blend").exists())

    def test_metadata_only_hidden_and_symlinks(self):
        self.add("public.txt", b"secret-in-content")
        self.add(".env", b"secret")
        self.add(".git/config")
        self.add("node_modules/pkg/index.js")
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "private.txt").write_text("not in project")
        (self.root / "outside-link").symlink_to(outside, target_is_directory=True)
        (self.root / "file-link").symlink_to(outside / "private.txt")
        self.assertEqual(self.scan()["indexed"], 1)
        self.assertEqual(discovery.search(self.db, "secret-in-content"), [])
        self.assertEqual([x["path"] for x in discovery.search(self.db)], ["public.txt"])

    def test_bounded_scan_preserves_previous_snapshot(self):
        old = self.add("old.txt")
        self.scan()
        old.unlink()
        self.add("a.txt")
        self.add("b.txt")
        with self.assertRaises(discovery.DiscoveryError):
            self.scan(max_entries=1)
        self.assertEqual([x["path"] for x in discovery.search(self.db)], ["old.txt"])
        with mock.patch.object(discovery, "collect", side_effect=OSError("unavailable")):
            with self.assertRaises(OSError):
                self.scan()
        self.assertEqual(discovery.projects(self.db)[0]["indexed"], 1)

    def test_no_broad_roots_or_silent_reassignment(self):
        for root in (Path("/"), Path.home(), self.base):
            with self.assertRaises(discovery.DiscoveryError):
                discovery.scan(self.db, "Demo", root)
        self.add("one.txt")
        self.scan()
        another = self.base / "other"
        another.mkdir()
        with self.assertRaises(discovery.DiscoveryError):
            discovery.scan(self.db, "Demo", another)
        with self.assertRaises(discovery.DiscoveryError):
            discovery.scan(self.db, "Other", self.root)
        self.assertEqual(discovery.projects(self.db)[0]["root"], str(self.root))

    def test_private_storage_and_foreign_schema(self):
        self.scan()
        self.assertEqual(self.db.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.db.stat().st_mode & 0o777, 0o600)
        with sqlite3.connect(self.db) as conn:
            conn.execute("PRAGMA user_version = 99")
        with self.assertRaises(discovery.DiscoveryError):
            discovery.projects(self.db)

    def test_refuse_symlink_or_insecure_index(self):
        self.db.parent.mkdir(mode=0o700)
        target = self.base / "target"
        target.write_text("leave me alone")
        self.db.symlink_to(target)
        with self.assertRaises(discovery.DiscoveryError):
            discovery.projects(self.db)
        self.assertEqual(target.read_text(), "leave me alone")
        self.db.unlink()
        self.db.parent.chmod(0o755)
        with self.assertRaises(discovery.DiscoveryError):
            discovery.projects(self.db)

    def test_folder_pages_and_indexed_open(self):
        for i in range(30):
            self.add("Models/item%02d.blend" % i)
        source = self.add("Reports/note.txt")
        self.add("launch.desktop")
        self.scan()
        root = discovery.folder_page(self.db, "Demo")
        self.assertEqual([x["name"] for x in root["entries"]], ["Models", "Reports", "launch.desktop"])
        self.assertEqual(len(discovery.folder_page(self.db, "Demo", "Models")["entries"]), 25)
        self.assertEqual(len(discovery.folder_page(self.db, "Demo", "Models", 25)["entries"]), 5)
        self.assertEqual(len(discovery.search(self.db, "item", limit=25, offset=25)), 5)
        for path in ("../secret", "/etc/passwd", "missing.txt"):
            with self.assertRaises(discovery.DiscoveryError):
                discovery.open_indexed(self.db, "Demo", path)
        with mock.patch.object(discovery.shutil, "which", return_value="/usr/bin/xdg-open"), mock.patch.object(discovery.subprocess, "Popen") as launch:
            discovery.open_indexed(self.db, "Demo", "Reports/note.txt")
            self.assertEqual(launch.call_args.args[0], ["/usr/bin/xdg-open", str(source)])
            discovery.open_indexed(self.db, "Demo", "launch.desktop", reveal=True)
            self.assertEqual(launch.call_args.args[0], ["/usr/bin/xdg-open", str(self.root)])
            with self.assertRaises(discovery.DiscoveryError):
                discovery.open_indexed(self.db, "Demo", "launch.desktop")
            source.chmod(0o700)
            with self.assertRaises(discovery.DiscoveryError):
                discovery.open_indexed(self.db, "Demo", "Reports/note.txt")
            source.unlink()
            source.symlink_to("/etc/passwd")
            with self.assertRaises(discovery.DiscoveryError):
                discovery.open_indexed(self.db, "Demo", "Reports/note.txt", reveal=True)

    def test_topology_empty_folders_and_migration(self):
        self.add("Models/Deep/tool.blend")
        (self.root / "Empty").mkdir()
        (self.root / "Models" / "EmptyChild").mkdir()
        (self.root / ".hidden").mkdir()
        self.scan()
        project = discovery.projects(self.db)[0]
        self.assertEqual(project["topology"], {"path":"", "name":"", "children":2,
            "folders":4, "endpoints":3, "depth":2, "complete":True})
        self.assertEqual([x["name"] for x in project["tree"]["entries"]], ["Empty","Models"])
        self.assertEqual(discovery.tree_page(self.db,"Demo","Models")["total"], 2)
        self.assertEqual(discovery.folder_page(self.db,"Demo","Empty")["entries"], [])
        with sqlite3.connect(self.db) as conn:
            conn.execute("DROP TABLE directories")
            conn.execute("DROP TABLE project_apps")
            conn.execute("DROP TABLE discovery_preferences")
            conn.execute("PRAGMA user_version=1")
        inferred = discovery.projects(self.db)[0]
        self.assertFalse(inferred["topology"]["complete"])
        self.assertEqual(inferred["topology"]["folders"], 2)
        self.assertEqual(inferred["indexed"], 1)
        self.scan()
        self.assertTrue(discovery.projects(self.db)[0]["topology"]["complete"])
        discovery.forget(self.db,"Demo")
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM directories").fetchone()[0],0)

    def test_preferences_and_project_association(self):
        self.assertEqual(discovery.preferences(self.db), {"launch_refresh":False})
        self.assertFalse(self.db.exists())
        self.add("Nested/source.kt")
        self.scan()
        discovery.set_preferences(self.db, True)
        self.assertTrue(discovery.preferences(self.db)["launch_refresh"])
        with self.assertRaises(discovery.DiscoveryError):
            discovery.associate(self.db,"Demo","arbitrary-command")
        with self.assertRaises(discovery.DiscoveryError):
            discovery.associate(self.db,"Demo","studio","../outside")
        discovery.associate(self.db,"Demo","studio","Nested")
        self.assertEqual(discovery.projects(self.db)[0]["association"], {"app":"studio","directory":"Nested"})
        with mock.patch.object(discovery,"app_command",return_value=["/usr/bin/studio"]), mock.patch.object(discovery.subprocess,"Popen") as launch:
            discovery.open_project(self.db,"Demo")
            self.assertEqual(launch.call_args.args[0],["/usr/bin/studio",str(self.root/"Nested")])
        self.scan()
        self.assertEqual(discovery.projects(self.db)[0]["association"]["app"],"studio")
        discovery.forget(self.db,"Demo")
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM project_apps").fetchone()[0],0)
        self.assertTrue(discovery.preferences(self.db)["launch_refresh"])

    def test_project_isolation_and_limits(self):
        self.add("first.txt")
        self.scan()
        second = self.base / "other"
        second.mkdir()
        (second / "second.txt").touch()
        discovery.scan(self.db, "Other", second)
        self.assertEqual(len(discovery.search(self.db)), 2)
        self.assertEqual(len(discovery.search(self.db, project="Demo")), 1)
        self.assertEqual(len(discovery.search(self.db, limit=1)), 1)
        with self.assertRaises(discovery.DiscoveryError):
            discovery.search(self.db, limit=201)
        discovery.forget(self.db, "Demo")
        self.assertEqual(discovery.search(self.db)[0]["project"], "Other")


if __name__ == "__main__":
    unittest.main()
