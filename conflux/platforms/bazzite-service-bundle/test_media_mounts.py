"""Simulated existing-service mount update tests. Never touch host services."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import service_manager as sm
import media_mounts as mounts


class MediaMountTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.old_root, self.old_units = sm.ROOT, sm.UNITS
        self.old_backup = mounts.BACKUP_DIR
        sm.ROOT = self.base / "home" / ".local" / "share" / "conflux-media-mirror"
        sm.UNITS = self.base / "home" / ".config" / "containers" / "systemd"
        mounts.BACKUP_DIR = self.base / "home" / ".local" / "state" / "quadlet-backups"
        mounts.PLANS.clear()
        sm.ROOT.mkdir(parents=True)
        sm.UNITS.mkdir(parents=True)
        self.ext = self.base / "external" / "Movies"
        self.ext.mkdir(parents=True)
        self.drive = self.ext.parent
        self.account = sm.ROOT / "state" / "jellyfin" / "config" / "test-account.db"
        self.account.parent.mkdir(parents=True)
        self.account.write_bytes(b"USER ACCOUNT DATABASE MUST STAY")
        for service in sm.SUPPORTED:
            sm.file_for(service).write_text(sm.unit_for(service), encoding="utf-8")
        self.original = sm.file_for("jellyfin").read_bytes()

        def fake_call(argv, timeout=25, max_chars=500):
            if argv[0] == "findmnt":
                payload = {"filesystems":[{"target":str(self.drive),
                    "source":"/dev/sdx1", "fstype":"ext4", "options":"rw"}]}
                return 0, json.dumps(payload)
            if argv[:3] == ["systemctl", "--user", "is-active"]:
                return 0, ""
            return 0, ""
        self.patchers = [
            mock.patch.object(sm, "on_bazzite", return_value=True),
            mock.patch.object(mounts.os, "geteuid", return_value=1000),
            mock.patch.object(mounts.shutil, "which", return_value="/usr/bin/findmnt"),
            mock.patch.object(mounts, "_call", side_effect=fake_call),
        ]
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patchers):
            patcher.stop()
        mounts.PLANS.clear()
        mounts.BACKUP_DIR = self.old_backup
        sm.ROOT, sm.UNITS = self.old_root, self.old_units
        self.tmp.cleanup()

    def test_preview_does_not_write_anything(self):
        plan = mounts.plan("jellyfin", "/media", str(self.ext))
        self.assertTrue(plan["will_change"])
        self.assertEqual(plan["destination"], "/media")
        self.assertIn("ro,nocreate", plan["preview"])
        self.assertEqual(sm.file_for("jellyfin").read_bytes(), self.original)
        self.assertFalse(mounts.BACKUP_DIR.exists())

    def test_apply_changes_only_media_mount_and_saves_old_unit(self):
        plan = mounts.plan("jellyfin", "/media", str(self.ext))
        result = mounts.apply(plan["plan_token"])
        self.assertTrue(result["restarted"])
        actual = sm.file_for("jellyfin").read_text()
        self.assertIn(f"Volume={self.ext}:/media:ro,nocreate", actual)
        self.assertIn("state/jellyfin/config:/config:Z", actual)
        self.assertEqual(self.account.read_bytes(), b"USER ACCOUNT DATABASE MUST STAY")
        self.assertEqual(Path(result["unit_backup"]).read_bytes(), self.original)
        self.assertEqual(sm.file_for("kavita").read_text(), sm.unit_for("kavita"))
        with self.assertRaises(ValueError):
            mounts.apply(plan["plan_token"])

    def test_stopped_service_is_not_started(self):
        def run(argv, timeout=25, max_chars=500):
            if argv[0] == "findmnt":
                return 0, json.dumps({"filesystems":[{"target":str(self.drive),
                  "source":"/dev/sdb1","fstype":"ext4","options":"rw"}]})
            if "is-active" in argv:
                return 3, "inactive"
            if "start" in argv or "restart" in argv:
                raise AssertionError("Updater must not start stopped service")
            return 0, ""
        with mock.patch.object(mounts, "_call", side_effect=run):
            result = mounts.apply(mounts.plan("navidrome", "/music", str(self.ext))["plan_token"])
        self.assertFalse(result["restarted"])

    def test_refuses_changed_unit_after_preview(self):
        plan = mounts.plan("jellyfin", "/media", str(self.ext))
        with sm.file_for("jellyfin").open("a") as out:
            out.write("# altered by user\n")
        with self.assertRaises(ValueError):
            mounts.apply(plan["plan_token"])
        self.assertIn("# altered by user", sm.file_for("jellyfin").read_text())

    def test_refuses_disconnected_drive_at_apply(self):
        plan = mounts.plan("jellyfin", "/media", str(self.ext))
        self.ext.rmdir()
        with self.assertRaises((ValueError, OSError)):
            mounts.apply(plan["plan_token"])
        self.assertEqual(sm.file_for("jellyfin").read_bytes(), self.original)

    def test_refuses_root_filesystem_not_external(self):
        def local_root(argv, timeout=25, max_chars=500):
            return 0, json.dumps({"filesystems":[{"target":"/",
                "source":"/dev/root","fstype":"btrfs","options":"rw"}]})
        with mock.patch.object(mounts, "_call", side_effect=local_root):
            with self.assertRaises(ValueError):
                mounts.plan("jellyfin", "/media", str(self.ext))

    def test_rejects_unsupported_destinations_and_whitespace(self):
        with self.assertRaises(ValueError):
            mounts.plan("jellyfin", "/config", str(self.ext))
        with self.assertRaises(ValueError):
            mounts.plan("navidrome", "/media", str(self.ext))
        with self.assertRaises(ValueError):
            mounts.plan("jellyfin", "/media", "/run/media/My Drive/Movies")
        self.assertFalse(mounts.BACKUP_DIR.exists())

    def test_no_manual_rw_media_overwrite(self):
        path = sm.file_for("kavita")
        path.write_text(path.read_text().replace(":ro,z", ":rw,z"), encoding="utf-8")
        with self.assertRaises(ValueError):
            mounts.plan("kavita", "/books", str(self.ext))

    def test_rollback_on_service_restart_failure(self):
        def error_on_restart(argv, timeout=25, max_chars=500):
            if argv[0] == "findmnt":
                return 0, json.dumps({"filesystems":[{"target":str(self.drive),
                  "source":"/dev/sdb1","fstype":"ext4","options":"rw"}]})
            if "restart" in argv:
                return 1, "simulated broken external mount"
            return 0, ""
        with mock.patch.object(mounts, "_call", side_effect=error_on_restart):
            plan = mounts.plan("jellyfin", "/media", str(self.ext))
            with self.assertRaises(RuntimeError):
                mounts.apply(plan["plan_token"])
        self.assertEqual(sm.file_for("jellyfin").read_bytes(), self.original)
        self.assertEqual(self.account.read_bytes(), b"USER ACCOUNT DATABASE MUST STAY")
        self.assertEqual(len(list(mounts.BACKUP_DIR.glob("*.bak"))), 1)

    def test_wont_rewrite_symlinked_quadlet(self):
        existing = sm.file_for("jellyfin")
        existing.unlink()
        separate = self.base / "somewhere-else"
        separate.write_text(sm.unit_for("jellyfin"))
        existing.symlink_to(separate)
        with self.assertRaises(ValueError):
            mounts.plan("jellyfin", "/media", str(self.ext))


if __name__ == "__main__":
    unittest.main()
