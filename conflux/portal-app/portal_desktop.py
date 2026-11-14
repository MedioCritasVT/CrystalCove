#!/usr/bin/env python3
"""One-click entry: reuse only this exact Portal checkout, never an old ZIP copy."""
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = os.environ.get("CONFLUX_PORTAL_PORT", "8765")
URL = "http://127.0.0.1:" + PORT


def running_portal_root():
    """Return actual running Conflux checkout, or None if the port isn't ours."""
    try:
        with urllib.request.urlopen(URL + "/api/status", timeout=0.6) as res:
            data = json.load(res)
        if data.get("mode") != "local-preview":
            return None
        # Older Portal versions had no source stamp. Do not confuse them with
        # the current checkout simply because their URL/port is the same.
        return data.get("portal_root") or "(older Portal, source unknown)"
    except (OSError, ValueError, TypeError):
        return None


def explain_port_conflict(running_root):
    message = (
        "A different Conflux Portal is already using " + URL +
        ". It was started from " + str(running_root) +
        ". Close that Portal process first, then start the Portal from " +
        str(ROOT) + ". Your browser Ledger and game files are not changed."
    )
    print(message, file=sys.stderr)
    # KDE / Bazzite users generally have kdialog. Show a visible explanation
    # rather than opening the wrong checkout or silently failing to bind.
    if shutil.which("kdialog"):
        subprocess.Popen(["kdialog", "--error", message, "--title",
                          "Conflux Portal"], start_new_session=True)
    elif shutil.which("zenity"):
        subprocess.Popen(["zenity", "--error", "--title=Conflux Portal",
                          "--text=" + message], start_new_session=True)


def main():
    current = running_portal_root()
    if current == str(ROOT):
        webbrowser.open(URL)
        return
    if current is not None:
        explain_port_conflict(current)
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
