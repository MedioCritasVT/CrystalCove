#!/usr/bin/env python3
"""One-click desktop entry: reuse the running Portal or start it quietly."""
import json
import os
import subprocess
import sys
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = os.environ.get("CONFLUX_PORTAL_PORT", "8765")
URL = "http://127.0.0.1:" + PORT


def running():
    try:
        with urllib.request.urlopen(URL + "/api/status", timeout=0.6) as res:
            return res.status == 200 and json.loads(res.read()).get("mode") == "local-preview"
    except (OSError, ValueError):
        return False


def main():
    if running():
        webbrowser.open(URL)
        return
    state = Path.home() / ".local" / "state" / "conflux-portal"
    state.mkdir(parents=True, exist_ok=True)
    log = state / "portal.log"
    with log.open("a", encoding="utf-8") as output:
        subprocess.Popen(
            [sys.executable, str(ROOT / "portal.py"), "--open-browser"],
            cwd=str(ROOT), start_new_session=True, stdin=subprocess.DEVNULL,
            stdout=output, stderr=subprocess.STDOUT, close_fds=True,
        )


if __name__ == "__main__":
    main()
