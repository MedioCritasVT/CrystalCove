#!/usr/bin/env python3
"""Conflux first-time-visitor browser journey; actual Portal, Chromium, and music.

Runs only from a dedicated CI step with Playwright installed. It does not start
the game, enable VOS, change Git, or overwrite the Architect's local data.
Live music test explicitly downloads the public GitHub Release album into a
temporary CI home, then verifies real media playback in the browser.
"""
import json
import os
import sys
import tempfile
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from playwright.sync_api import sync_playwright

def main():
    with tempfile.TemporaryDirectory(prefix="conflux-browser-review-") as home:
        os.environ["XDG_DATA_HOME"] = str(Path(home) / "data")
        os.environ["XDG_CONFIG_HOME"] = str(Path(home) / "config")
        import portal

        # Do not accidentally use a real user's game registrations or app data.
        portal.CONFIG = Path(home) / "apps.json"
        srv = ThreadingHTTPServer(("127.0.0.1", 0), portal.Handler)
        worker = threading.Thread(target=srv.serve_forever, daemon=True)
        worker.start()
        base = f"http://127.0.0.1:{srv.server_port}"
        proof = APP / "browser-proof"
        proof.mkdir(exist_ok=True)
        observations = []
        errors = []
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(channel="chrome", headless=True,
                    args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"])
                context = browser.new_context(viewport={"width":1440,"height":940},
                                              accept_downloads=True)
                page = context.new_page()
                page.on("pageerror", lambda exc: errors.append(str(exc)))
                page.goto(base, wait_until="domcontentloaded", timeout=25000)
                page.locator("#home h2").wait_for(state="visible")
                page.screenshot(path=str(proof / "01-threshold.png"), full_page=True)
                observations.append("Threshold loads; no VOS service or game starts")
                assert page.locator("#music-toggle").get_attribute("aria-pressed") == "false"

                page.locator('button[data-page="nodes"]').click()
                page.locator("#nodes h2").wait_for(state="visible")
                assert page.locator("#node-list .node-card").count() == 5
                for node in ["medio", "ratio", "nexus", "specula", "limen"]:
                    pet = page.locator(f'#node-list .pet-token[data-node="{node}"]')
                    assert pet.count() == 1, f"missing {node}"
                    assert pet.locator(".pet-face .pet-eye").count() == 2
                    assert page.locator(f'.pet-token[data-node="{node}"] .pet-bodice').count() >= 1
                medio_hair = page.locator('#node-list .pet-token[data-node="medio"]').evaluate(
                    "(e) => getComputedStyle(e).getPropertyValue('--pet-hair').trim()")
                limen_hair = page.locator('#node-list .pet-token[data-node="limen"]').evaluate(
                    "(e) => getComputedStyle(e).getPropertyValue('--pet-hair').trim()")
                assert medio_hair != limen_hair, "independent character palettes"
                page.screenshot(path=str(proof / "02-node-companions.png"), full_page=True)
                observations.append("Five source-linked chibis have distinct hair, face and costume layers")

                page.locator('button[data-page="guide"]').click()
                page.locator("#project-readme h2, #project-readme h3").first.wait_for(timeout=15000)
                assert page.locator('#guide a:has-text("View the portable Markdown Player Manual")').count() == 0
                page.screenshot(path=str(proof / "03-player-manual.png"), full_page=True)
                observations.append("Installed README renders in Player Manual; no redundant outdated manual link")

                # External choices should never auto-open merely when link is visible.
                page.locator("nav a.nav-external").click()
                page.locator("#open-choice-dialog[open]").wait_for()
                assert len(context.pages) == 1, "must prompt before opening external page"
                page.locator("#open-choice-cancel").click()
                assert len(context.pages) == 1, "cancel must not navigate"
                observations.append("New tab/window/cancel choice prompts; cancel leaves Portal intact")

                page.locator('button[data-page="soundtrack"]').click()
                page.screenshot(path=str(proof / "04-soundtrack-catalog.png"), full_page=True)
                assert page.locator("#music-toggle").get_attribute("aria-pressed") == "false"
                observations.append("Soundtrack inventory accessible with music initially off")

                # Live public-release install under an isolated throwaway CI home.
                page.locator(".music-advanced summary").click()
                install = page.locator("#music-install-public")
                install.click()
                page.get_by_text("Downloaded and checksum-verified 11 recordings", exact=False).wait_for(timeout=90000)
                rows = page.locator("#music-select option").count()
                assert rows >= 10, f"expected ten music compositions, got {rows}"
                observations.append("Official 11-track GitHub Release installs into an isolated user library")

                # Music On itself starts playback. Do not immediately click
                # Play a second time: it becomes Pause once audio is playing.
                page.locator("#music-toggle").click()
                page.wait_for_function("() => {const a=document.querySelector('#music-audio');return !a.paused && a.currentTime>0.8;}", timeout=18000)
                page.wait_for_timeout(1400)
                media = page.locator("#music-audio").evaluate(
                    "(e) => ({paused:e.paused,time:e.currentTime,ready:e.readyState,"
                    "source:e.currentSrc,error:e.error?.message || null})")
                assert media["time"] > 0.8 and not media["paused"], f"real MP3 playback failed: {media}"
                page.screenshot(path=str(proof / "05-music-while-exploring.png"), full_page=True)
                page.locator('button[data-page="home"]').click()
                page.wait_for_timeout(1200)
                after = page.locator("#music-audio").evaluate(
                    "(e) => ({paused:e.paused,time:e.currentTime})")
                assert not after["paused"] and after["time"] > media["time"], (
                    f"music should continue during navigation: {media} -> {after}")
                page.screenshot(path=str(proof / "06-home-with-music.png"), full_page=True)
                observations.append("Actual Conflux MP3 time advances; music persists while navigating")
                page.locator("#music-toggle").click()
                assert page.locator("#music-audio").evaluate("(e) => e.paused")
                observations.append("Music-off control pauses playback")

                if errors:
                    raise AssertionError("Unexpected browser page errors: " + " | ".join(errors))
                (proof / "review.json").write_text(json.dumps({
                    "observations":observations,"errors":errors,
                    "medio_hair":medio_hair,"limen_hair":limen_hair,
                    "playback_time":media["time"],"playback_after_navigation":after["time"],
                    "scope":"Automated browser journey, not a human hearing assessment",
                },indent=2)+"\n",encoding="utf-8")
                for item in observations: print("PASS:",item,flush=True)
                browser.close()
        finally:
            srv.shutdown()
            srv.server_close()
            worker.join(timeout=5)
    return 0

if __name__ == "__main__":
    sys.exit(main())
