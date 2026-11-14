#!/usr/bin/env python3
"""Screenshot the real local Portal's Node Companions page for README examples.

Runs on a clean, temporary loopback server. Does not launch Unreal, enable
music, access private browser profiles, or alter local app settings.
"""
from __future__ import annotations

import os
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

APP = Path(__file__).resolve().parents[2] / "conflux" / "portal-app"
sys.path.insert(0, str(APP))


def main():
    output = Path(__file__).resolve().parent / "05-node-companions.png"
    with tempfile.TemporaryDirectory(prefix="conflux-readme-nodes-") as user_home:
        os.environ["XDG_DATA_HOME"] = str(Path(user_home) / "data")
        os.environ["XDG_CONFIG_HOME"] = str(Path(user_home) / "config")
        import portal

        portal.CONFIG = Path(user_home) / "apps.json"
        server = ThreadingHTTPServer(("127.0.0.1", 0), portal.Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    channel="chrome", headless=True, args=["--no-sandbox"])
                page = browser.new_page(
                    viewport={"width": 1420, "height": 1030},
                    device_scale_factor=1,
                    reduced_motion="reduce",
                )
                page.goto("http://127.0.0.1:" + str(server.server_port),
                          wait_until="domcontentloaded", timeout=30000)
                page.locator('nav button[data-page="nodes"]').click()
                page.locator("#node-list .node-card").first.wait_for()
                assert page.locator("#node-list .node-card").count() == 5
                # The music dock is hidden ONLY for this documentation crop.
                # Normal visitors still see the original optional dock.
                page.add_style_tag(content="""
                    #music-dock,.music-dock {display:none !important;}
                    #nodes .node-card {break-inside:avoid;}
                """)
                page.locator("#nodes").screenshot(
                    path=str(output),
                    animations="disabled",
                    timeout=30000,
                )
                browser.close()
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)
    # Keep README media reasonably light without losing chibi details.
    with Image.open(output) as image:
        image = image.convert("RGB")
        if image.width > 1100:
            image.thumbnail((1100, 1250))
        image.save(output, optimize=True)
    print(f"Captured five live Portal Node companions: {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
