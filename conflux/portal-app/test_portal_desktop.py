"""Protect the Bazzite desktop entry from opening a different running checkout."""
import io
import json
import unittest
from unittest import mock

import portal_desktop


class DesktopCheckoutIdentityTests(unittest.TestCase):
    def test_running_portal_identifies_exact_checkout(self):
        output = {"mode": "local-preview", "portal_root": str(portal_desktop.ROOT)}
        with mock.patch.object(portal_desktop.urllib.request, "urlopen",
                               return_value=io.BytesIO(json.dumps(output).encode())):
            self.assertEqual(portal_desktop.running_portal_root(),
                             str(portal_desktop.ROOT))

    def test_older_portal_is_not_mistaken_for_current(self):
        data = {"mode": "local-preview"}
        with mock.patch.object(portal_desktop.urllib.request, "urlopen",
                               return_value=io.BytesIO(json.dumps(data).encode())):
            self.assertIn("older Portal", portal_desktop.running_portal_root())

    def test_desktop_entry_reuses_only_identical_source(self):
        with mock.patch.object(portal_desktop, "running_portal_root",
                               return_value=str(portal_desktop.ROOT)):
            with mock.patch.object(portal_desktop.webbrowser, "open") as browser:
                with mock.patch.object(portal_desktop.subprocess, "Popen") as spawn:
                    portal_desktop.main()
                    browser.assert_called_once_with(portal_desktop.URL)
                    spawn.assert_not_called()

    def test_another_zip_portal_blocks_silent_reuse_and_new_server(self):
        with mock.patch.object(portal_desktop, "running_portal_root",
                               return_value="/home/guest/CrystalCove-main/conflux/portal-app"):
            with mock.patch.object(portal_desktop, "explain_port_conflict") as explanation:
                with mock.patch.object(portal_desktop.webbrowser, "open") as browser:
                    with mock.patch.object(portal_desktop.subprocess, "Popen") as spawn:
                        portal_desktop.main()
                        explanation.assert_called_once()
                        browser.assert_not_called()
                        spawn.assert_not_called()


if __name__ == "__main__":
    unittest.main()
