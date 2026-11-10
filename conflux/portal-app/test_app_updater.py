"""Real local Git integration tests: no network and no user files touched."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app_updater
from app_updater import UpdateError, UpdateManager
from install_desktop_launcher import install_desktop_launcher


def git(*args):
    p = subprocess.run(["git", *map(str, args)], capture_output=True,
                       text=True, timeout=15, check=False)
    if p.returncode:
        raise AssertionError("git " + " ".join(map(str, args)) +
                             ": " + p.stderr)
    return p.stdout.strip()


class GitSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bare = self.root / "origin.git"
        self.writer = self.root / "writer"
        self.client = self.root / "local"
        git("init", "--bare", "-b", "main", self.bare)
        git("init", "-b", "main", self.writer)
        git("-C", self.writer, "config", "user.name", "Portal Test")
        git("-C", self.writer, "config", "user.email", "portal@example.invalid")
        self.write(self.writer, "conflux/portal-app/portal.py", "# v1\n")
        self.write(self.writer, ".obsidian/workspace.json", '{"layout":"mine"}\n')
        git("-C", self.writer, "add", ".")
        git("-C", self.writer, "commit", "-m", "Baseline")
        git("-C", self.writer, "remote", "add", "origin", self.bare)
        git("-C", self.writer, "push", "origin", "main")
        git("clone", "--branch", "main", self.bare, self.client)
        # The checkout reports an official GitHub origin, while the fetch URL
        # is patched to a temporary local bare repo for safety and determinism.
        git("-C", self.client, "remote", "set-url", "origin",
            "git@github.com:MedioCritasVT/CrystalCove.git")
        self.patch_repo = patch.object(app_updater, "REPOSITORY", str(self.bare))
        self.patch_repo.start()
        self.addCleanup(self.patch_repo.stop)
        self.manager = UpdateManager(self.client)

    @staticmethod
    def write(root, name, content):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def commit_remote(self, path="conflux/portal-app/portal.py", content="# v2\n"):
        self.write(self.writer, path, content)
        git("-C", self.writer, "add", ".")
        git("-C", self.writer, "commit", "-m", "Update")
        git("-C", self.writer, "push", "origin", "main")

    def test_check_up_to_date_does_not_modify_working_files(self):
        local = self.client / ".obsidian" / "workspace.json"
        local.write_text('{"layout":"custom"}\n', encoding="utf-8")
        data = self.manager.check()
        self.assertEqual(data["status"], "current")
        self.assertFalse(data["can_apply"])
        self.assertEqual(local.read_text(), '{"layout":"custom"}\n')

    def test_updates_preserve_unrelated_modified_obsidian_files(self):
        self.commit_remote()
        local = self.client / ".obsidian" / "workspace.json"
        local.write_text('{"layout":"custom"}\n', encoding="utf-8")
        data = self.manager.check()
        self.assertEqual(data["status"], "available")
        self.assertTrue(data["can_apply"])
        self.assertEqual(local.read_text(), '{"layout":"custom"}\n')
        applied = self.manager.apply()
        self.assertTrue(applied["updated"])
        self.assertTrue(applied["relaunch"])
        self.assertEqual((self.client / "conflux/portal-app/portal.py").read_text(), "# v2\n")
        self.assertEqual(local.read_text(), '{"layout":"custom"}\n')
        self.assertIn(".obsidian/workspace.json", git("-C", self.client, "status", "--short"))

    def test_overlapping_local_changes_are_not_overwritten(self):
        self.commit_remote(path=".obsidian/workspace.json", content='{"layout":"remote"}\n')
        local = self.client / ".obsidian" / "workspace.json"
        local.write_text('{"layout":"custom"}\n', encoding="utf-8")
        self.manager.check()
        with self.assertRaises(UpdateError):
            self.manager.apply()
        self.assertEqual(local.read_text(), '{"layout":"custom"}\n')
        self.assertEqual(git("-C", self.client, "rev-parse", "HEAD"),
                         git("-C", self.writer, "rev-parse", "HEAD~1"))

    def test_can_switch_from_review_branch_without_forcing_files(self):
        git("-C", self.client, "switch", "-c", "portal-review")
        local = self.client / ".obsidian" / "workspace.json"
        local.write_text('{"layout":"review"}\n', encoding="utf-8")
        data = self.manager.check()
        self.assertEqual(data["status"], "switch")
        self.assertTrue(data["needs_switch"])
        self.manager.apply()
        self.assertEqual(git("-C", self.client, "branch", "--show-current"), "main")
        self.assertEqual(local.read_text(), '{"layout":"review"}\n')

    def test_different_origin_is_rejected(self):
        git("-C", self.client, "remote", "set-url", "origin", self.bare)
        with self.assertRaisesRegex(UpdateError, "not the official"):
            self.manager.check()

    def test_divergence_refused(self):
        self.commit_remote()
        git("-C", self.client, "config", "user.name", "Portal Test")
        git("-C", self.client, "config", "user.email", "portal@example.invalid")
        self.write(self.client, "local.txt", "local commit\n")
        git("-C", self.client, "add", "local.txt")
        git("-C", self.client, "commit", "-m", "Local divergence")
        old_head = git("-C", self.client, "rev-parse", "HEAD")
        with self.assertRaisesRegex(UpdateError, "cannot be fast-forwarded"):
            self.manager.check()
        self.assertEqual(git("-C", self.client, "rev-parse", "HEAD"), old_head)

    def test_apply_requires_explicit_prior_check(self):
        with self.assertRaisesRegex(UpdateError, "Check for Updates"):
            self.manager.apply()


class DesktopEntryTests(unittest.TestCase):
    def test_user_only_desktop_entry(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict(os.environ, {"XDG_DATA_HOME": temp}):
                location = Path(install_desktop_launcher())
                self.assertTrue(location.is_file())
                content = location.read_text(encoding="utf-8")
                self.assertIn("Name=Conflux Portal", content)
                self.assertIn("Terminal=false", content)
                self.assertIn("portal_desktop.py", content)
                self.assertIn("Exec=", content)
                self.assertEqual(location.stat().st_mode & 0o777, 0o644)

    def test_symlink_desktop_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "applications"
            folder.mkdir()
            (folder / "conflux-portal.desktop").symlink_to(Path(temp) / "other.desktop")
            with patch.dict(os.environ, {"XDG_DATA_HOME": temp}):
                with self.assertRaises(OSError):
                    install_desktop_launcher()


if __name__ == "__main__":
    unittest.main()
