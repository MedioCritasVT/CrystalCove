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
