"""Safe standard-library smoke tests for the local Conflux Portal.

Run from conflux/portal-app: python3 -m unittest test_portal.py -v
No game or external application is executed.
"""
import json
import os
import shutil
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer

import portal


class PortalSmokeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.original_config = portal.CONFIG
        portal.CONFIG = Path(self.tmp.name) / "apps.json"
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), portal.Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = "http://127.0.0.1:" + str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        portal.CONFIG = self.original_config
        self.tmp.cleanup()

    def get(self, path):
        with urlopen(self.base + path, timeout=3) as response:
            return response.status, response.read().decode("utf-8")

    def test_home_and_scripts_are_served(self):
        status, html = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn('id="home"', html)
        self.assertIn('id="guide"', html)
        self.assertIn("Journey progress is not automatically saved", html)
        status, js = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn('button.dataset.page', js)

    def test_bundled_apps_open(self):
        for route, expected in (("/apps/atelier", "Conflux · The Atelier"),
                                ("/apps/ledger", "Conflux Ledger")):
            status, html = self.get(route)
            self.assertEqual(status, 200)
            self.assertIn(expected, html)
            self.assertIn("<script", html)

    def test_unconfigured_catalog_states(self):
        _, body = self.get("/api/status")
        data = json.loads(body)
        by_id = {item["id"]: item for item in data["apps"]}
        self.assertEqual(by_id["conflux-game"]["action"], "download")
        self.assertEqual(by_id["conflux-atelier"]["action"], "open")
        self.assertEqual(by_id["conflux-ledger"]["action"], "open")
        self.assertEqual(data["vos"], "not-connected")

    def test_configured_game_is_launchable_but_not_started_by_test(self):
        executable = Path(self.tmp.name) / "mock-game.sh"
        executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        executable.chmod(0o700)
        portal.CONFIG.write_text(json.dumps([{
            "id": "conflux-game", "name": "Mock", "executable": str(executable)
        }]), encoding="utf-8")
        _, body = self.get("/api/status")
        by_id = {item["id"]: item for item in json.loads(body)["apps"]}
        self.assertEqual(by_id["conflux-game"]["action"], "launch")
        self.assertTrue(by_id["conflux-game"]["installed"])
        self.assertEqual(by_id["conflux-atelier"]["action"], "open")

    def test_launch_requires_valid_origin_and_token(self):
        body = json.dumps({"id": "conflux-game"}).encode("utf-8")
        request = Request(self.base + "/api/launch", data=body, method="POST",
                          headers={"Content-Type": "application/json"})
        with self.assertRaises(HTTPError) as err:
            urlopen(request, timeout=3)
        self.assertEqual(err.exception.code, 403)

        request = Request(self.base + "/api/launch", data=body, method="POST",
                          headers={"Content-Type": "application/json",
                                   "Origin": self.base,
                                   "X-Conflux-Token": portal.TOKEN})
        with self.assertRaises(HTTPError) as err:
            urlopen(request, timeout=3)
        self.assertEqual(err.exception.code, 404)

    @unittest.skipUnless(shutil.which("node"), "Node.js not installed; browser syntax check skipped")
    def test_javascript_syntax(self):
        script = Path(__file__).with_name("app.js")
        result = subprocess.run(["node", "--check", str(script)],
                                text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
