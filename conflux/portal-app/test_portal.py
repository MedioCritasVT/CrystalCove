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
from unittest import mock

import game_locator

import portal


class PortalSmokeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        portal.SUGGESTIONS.clear()
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


    def post(self, path, payload):
        data = json.dumps(payload).encode("utf-8")
        request = Request(self.base + path, data=data, method="POST",
                          headers={"Content-Type": "application/json",
                                   "Origin": self.base,
                                   "X-Conflux-Token": portal.TOKEN})
        with urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def test_download_page_and_palettes(self):
        status, html = self.get("/downloads")
        self.assertEqual(status, 200)
        self.assertIn('id="downloads"', html)
        self.assertIn('id="game-browse"', html)
        self.assertIn('id="game-folder-input"', html)
        self.assertIn('id="game-find"', html)
        self.assertIn("Conflux-V0.1-Linux-x86_64.tar.gz", html)
        self.assertIn("--amber:#e9bf84", html)
        self.assertIn("--violet:#c2a4f3", html)
        self.assertIn("--blue:#84bff3", html)
        self.assertIn("--green:#9cdec0", html)

    def test_bounded_folder_search_and_explicit_registration(self):
        game = Path(self.tmp.name) / "Games" / "V0.1"
        game.mkdir(parents=True)
        launcher = game / "PlayConflux.sh"
        launcher.write_text("#!/bin/sh\\nexit 0\\n", encoding="utf-8")
        launcher.chmod(0o700)
        status, data = self.post("/api/game/find", {"directory": str(Path(self.tmp.name))})
        self.assertEqual(status, 200)
        self.assertEqual(len(data["candidates"]), 1)
        self.assertEqual(data["candidates"][0]["path"], str(launcher))
        self.assertTrue(data["candidates"][0]["ready"])
        self.assertFalse(portal.CONFIG.exists(), "Inspection must not register anything")
        status, out = self.post("/api/game/register", {"path": str(launcher)})
        self.assertEqual(status, 200)
        self.assertTrue(out["registered"])
        self.assertEqual(out["apps"][0]["action"], "launch")
        saved = json.loads(portal.CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(saved[0]["executable"], str(launcher))
        self.assertEqual(portal.CONFIG.stat().st_mode & 0o777, 0o600)

    def test_registration_requires_a_fresh_inspection(self):
        game = Path(self.tmp.name) / "PlayConflux.sh"
        game.write_text("#!/bin/sh\\nexit 0\\n", encoding="utf-8")
        game.chmod(0o700)
        with self.assertRaises(HTTPError) as err:
            self.post("/api/game/register", {"path": str(game)})
        self.assertEqual(err.exception.code, 400)
        self.assertFalse(portal.CONFIG.exists())

    def test_nonexistent_folder_is_rejected(self):
        with self.assertRaises(HTTPError) as err:
            self.post("/api/game/find", {"directory": str(Path(self.tmp.name) / "missing")})
        self.assertEqual(err.exception.code, 400)

    def test_symlink_launchers_are_not_suggested(self):
        src = Path(self.tmp.name) / "elsewhere.sh"
        src.write_text("#!/bin/sh\\nexit 0\\n", encoding="utf-8")
        src.chmod(0o700)
        root = Path(self.tmp.name) / "Game"
        root.mkdir()
        (root / "PlayConflux.sh").symlink_to(src)
        results = game_locator.scan_folder(str(root))
        self.assertEqual(results["candidates"], [])

    def test_picker_cancel_does_not_register(self):
        with mock.patch("game_locator.picker_program",
                        return_value=("kdialog", "/usr/bin/kdialog")):
            with mock.patch("game_locator.subprocess.run") as run:
                run.return_value.returncode = 1
                run.return_value.stdout = ""
                _, data = self.post("/api/game/browse", {})
                self.assertTrue(data["cancelled"])
                self.assertFalse(portal.CONFIG.exists())
                self.assertEqual(run.call_args.args[0][0], "/usr/bin/kdialog")

    def test_protect_other_app_config(self):
        game = Path(self.tmp.name) / "PlayConflux.sh"
        game.write_text("#!/bin/sh\\nexit 0\\n", encoding="utf-8")
        game.chmod(0o700)
        portal.CONFIG.write_text(json.dumps([{
            "id": "my-local-tool", "name": "Private tool",
            "executable": "/usr/bin/true"
        }]), encoding="utf-8")
        self.post("/api/game/find", {"directory": self.tmp.name})
        self.post("/api/game/register", {"path": str(game)})
        entries = json.loads(portal.CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["id"], "my-local-tool")

    @unittest.skipUnless(shutil.which("node"), "Node.js not installed; browser syntax check skipped")
    def test_javascript_syntax(self):
        script = Path(__file__).with_name("app.js")
        result = subprocess.run(["node", "--check", str(script)],
                                text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
