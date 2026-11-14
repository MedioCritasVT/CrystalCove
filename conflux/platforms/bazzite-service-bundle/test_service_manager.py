"""Offline, non-mutating tests; no Podman images or services required."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import service_manager as sm

class ServiceManagerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.root = sm.ROOT
        self.units = sm.UNITS
        sm.ROOT = self.home / "local" / "mirror"
        sm.UNITS = self.home / "config" / "containers" / "systemd"
        sm._issued.clear()

    def tearDown(self):
        sm.ROOT = self.root
        sm.UNITS = self.units
        self.tmp.cleanup()

    def ready(self):
        info={"ID":"bazzite","PRETTY_NAME":"Bazzite"}
        def fake_run(argv, timeout=12):
            return (True,"true")
        with mock.patch.object(sm,"read_os_release",return_value=info), \
             mock.patch.object(sm,"command_available",return_value=True), \
             mock.patch.object(sm,"run_readonly",side_effect=fake_run), \
             mock.patch.object(sm,"port_free",return_value=True):
            return sm.issue_plan()

    def test_reports_bazzite_only(self):
        self.assertTrue(sm.on_bazzite({"VARIANT_ID":"bazzite"}))
        self.assertFalse(sm.on_bazzite({"ID":"cachyos"}))

    def test_quads_loopback_and_media_read_only(self):
        for name in sm.SUPPORTED:
            unit=sm.unit_for(name)
            self.assertIn("PublishPort=127.0.0.1:",unit)
            self.assertIn(":ro,z",unit)
            self.assertNotIn("AutoUpdate=registry",unit)
            self.assertNotIn("Password=",unit)

    def test_plan_fails_if_any_existing_data(self):
        (sm.ROOT/"state"/"jellyfin").mkdir(parents=True)
        plan=self.ready()
        self.assertFalse(plan["ready"])
        self.assertNotIn("plan_token",plan)

    def test_plan_cannot_be_reused(self):
        plan=self.ready()
        with mock.patch.object(sm,"summarize",return_value={"ready":True}), \
             mock.patch.object(sm,"run_readonly",return_value=(True,"")):
            result=sm.install(plan["plan_token"],"INSTALL NEW BAZZITE MIRROR")
            self.assertEqual(len(result["installed_files"]),3)
            with self.assertRaises(ValueError):
                sm.install(plan["plan_token"],"INSTALL NEW BAZZITE MIRROR")

    def test_plan_requires_explicit_phrase(self):
        plan=self.ready()
        with self.assertRaises(ValueError):
            sm.install(plan["plan_token"],"sure")
        self.assertFalse(sm.UNITS.exists())

    def test_port_conflict_blocked(self):
        with mock.patch.object(sm,"read_os_release",return_value={"ID":"bazzite"}), \
             mock.patch.object(sm,"command_available",return_value=True), \
             mock.patch.object(sm,"run_readonly",return_value=(True,"")), \
             mock.patch.object(sm,"port_free",return_value=False):
            self.assertNotIn("plan_token",sm.issue_plan())

    def test_unit_file_conflict_prevents_plan(self):
        sm.UNITS.mkdir(parents=True)
        sm.file_for("kavita").write_text("owned by someone else")
        self.assertFalse(self.ready()["ready"])

if __name__ == "__main__":
    unittest.main()
