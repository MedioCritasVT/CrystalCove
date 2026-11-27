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
        os.environ["XDG_STATE_HOME"] = str(Path(home) / "state")
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
                # The three bundled OFL fonts must actually load on Linux,
                # not just appear as decorative names in a CSS declaration.
                fonts=page.evaluate("""async () => {
                  const families=["Conflux Marcellus","Conflux Source Sans 3",
                                  "Conflux JetBrains Mono"];
                  const result={};
                  for (const family of families) {
                    const loaded=await document.fonts.load('16px "'+family+'"');
                    result[family]={loaded:loaded.length,
                                    present:document.fonts.check('16px "'+family+'"')};
                  }
                  return result;
                }""")
                assert all(item["loaded"]>=1 and item["present"] for item in fonts.values()), (
                    "one or more offline Portal fonts failed to load: "+str(fonts))
                assert "Conflux Source Sans 3" in page.locator("body").evaluate(
                    "(e)=>getComputedStyle(e).fontFamily")
                assert "Conflux Marcellus" in page.locator("#home h2").evaluate(
                    "(e)=>getComputedStyle(e).fontFamily")
                assert "Conflux JetBrains Mono" in page.locator("#music-elapsed").evaluate(
                    "(e)=>getComputedStyle(e).fontFamily")

                page.screenshot(path=str(proof / "01-threshold.png"), full_page=True)
                observations.append("Threshold loads; no VOS service or game starts")
                assert page.locator("#music-toggle").get_attribute("aria-pressed") == "false"
                # Navigation is functional, not Node-gated. Verify visual
                # hierarchy, room switching, steward labels, and motion safety.
                assert page.locator(".nav-group").count() == 4
                assert page.locator(".nav-group[data-group='begin'] button").count() == 3
                assert page.locator(".nav-group[data-group='discover'] button").count() == 6
                assert page.locator(".nav-group[data-group='create'] button").count() == 4
                assert page.locator(".nav-group[data-group='maintain'] button").count() == 2
                assert page.locator(".portal-nav button[data-page]").count() == 15
                glyphs=page.locator(".portal-nav button[data-page] .nav-symbol")
                assert glyphs.count()==15
                assert page.locator(".portal-nav .nav-glyph").count()==15
                for index in range(glyphs.count()):
                    tile=glyphs.nth(index).bounding_box()
                    ink=page.locator(".portal-nav .nav-glyph").nth(index).bounding_box()
                    assert tile and ink
                    centers=abs((tile["x"]+tile["width"]/2)-(ink["x"]+ink["width"]/2))
                    assert centers<2.6, "room glyph is optically outside its tile"

                for index in range(glyphs.count()):
                    glyph=glyphs.nth(index)
                    bounds=glyph.bounding_box()
                    assert bounds and bounds["width"]>=28 and bounds["height"]>=28, (
                        "sidebar symbol should not shrink or disappear")
                    assert glyph.get_attribute("aria-hidden")=="true"
                assert page.locator(".side .brand-symbol").count()==1
                assert page.locator("#music-prev").get_attribute("aria-label")=="Previous track"
                assert page.locator("#music-next").get_attribute("aria-label")=="Next track"
                assert page.locator("#music-visual-close").get_attribute("aria-label")=="Close visualizer"
                assert page.locator(".external-glyph").count()>=15

                assert page.locator("#room-companion-home .pet-duty").count() == 2
                assert page.locator("#room-companion-home .pet-duty").first.inner_text().startswith("Medio")
                page.locator(".nav-stewards summary").click()
                assert "Observation" in page.locator(".nav-stewards").inner_text()
                page.locator(".nav-stewards summary").click()
                for destination in ("guide","nodes","library","apps","vos","updates"):
                    page.locator(f'button[data-page="{destination}"]').click()
                    assert page.locator(f"#{destination}").is_visible()
                    assert page.locator(f'button[data-page="{destination}"]').get_attribute("aria-current") == "page"
                page.locator('button[data-page="discovery"]').click()
                page.locator("#discovery-projects").get_by_text("No projects registered.", exact=False).wait_for()
                assert not portal.discovery_index.default_db().exists()
                project = Path(home) / "discovery-fixture"
                project.mkdir()
                (project / "sample.blend").write_bytes(b"fixture")
                page.locator("#discovery-name").fill("Browser fixture")
                page.locator("#discovery-root").fill(str(project))
                page.locator("#discovery-register button[type=submit]").click()
                page.locator("#discovery-results").get_by_text("sample.blend", exact=True).wait_for()
                assert (project / "sample.blend").read_bytes() == b"fixture"
                page.locator("#discovery-projects").get_by_role("button", name="▸ Browse folders").click()
                page.locator("#discovery-breadcrumb").get_by_role("button", name="Browser fixture").wait_for()
                page.locator("#discovery-results").get_by_text("sample.blend", exact=True).wait_for()
                page.locator("#discovery-query").fill("nonexistent")
                page.locator("#discovery-search button").click()
                page.locator("#discovery-results").get_by_text("No matching indexed files.").wait_for()
                page.once("dialog", lambda dialog: dialog.accept())
                page.locator("#discovery-projects").get_by_role("button", name="Forget index").click()
                page.locator("#discovery-projects").get_by_text("No projects registered.", exact=False).wait_for()
                assert (project / "sample.blend").exists()
                observations.append("Discovery registers and searches a disposable project; forgetting preserves source files")
                page.locator('button[data-page="nodes"]').click()
                assert page.locator("#node-list .node-portal-duty").count() == 5
                nexus=page.locator('#node-list .pet-token[data-node="nexus"] .pet-mark')
                assert nexus.is_visible()
                nx=nexus.bounding_box()
                assert nx and nx["width"]>=29 and nx["height"]>=24
                nexus_mark=nexus.evaluate("(el)=>getComputedStyle(el,'::before').backgroundImage")
                assert "data:image/svg+xml" in nexus_mark, "Nexus loop needs a sharp, font-independent shape"

                emblem=page.locator("#node-list .pet-token .pet-mark").first
                assert emblem.evaluate("(e)=>parseFloat(getComputedStyle(e).fontSize)")>=14

                detail = page.locator('#node-list .pet-token[data-node="ratio"]')
                assert detail.evaluate("(e)=>getComputedStyle(e,'::after').content") != "none"
                jewel = page.locator('#node-list .pet-token[data-node="nexus"] .pet-chest-jewel')
                assert jewel.evaluate("(e)=>getComputedStyle(e,'::before').content") != "none"
                page.emulate_media(reduced_motion="reduce")
                assert page.locator('#room-companion-nodes .pet-token').first.evaluate(
                    "(e)=>getComputedStyle(e,'::after').animationName") == "none"
                page.emulate_media(reduced_motion="no-preference")
                page.emulate_media(reduced_motion="reduce")
                assert page.locator("#nodes .room-hero").evaluate(
                    "(el) => getComputedStyle(el).animationName") == "none"
                page.emulate_media(reduced_motion="no-preference")
                page.locator('button[data-page="home"]').click()
                # Render and exercise a narrow viewport without any clone,
                # external login, launch or write action.
                small=context.new_page()
                small.set_viewport_size({"width":390,"height":844})
                small.goto(base,wait_until="domcontentloaded")
                assert small.locator(".nav-group").count() == 4
                nav_mark=small.locator('.nav-group[data-group="begin"] .nav-symbol').first.bounding_box()
                assert nav_mark and nav_mark["width"]>=25 and nav_mark["height"]>=25, (
                    "mobile symbol needs a comfortably legible tile")
                assert small.locator(".nav-utilities .utility-symbol").count()==1

                small.locator('button[data-page="studio"]').click()
                assert small.locator("#studio").is_visible()
                small.screenshot(path=str(proof / "01-wayfinding-mobile.png"),full_page=True)
                small.locator("#music-visual-toggle").click()
                assert small.locator("#music-visual-panel").is_visible()
                md = small.locator("#music-dock").bounding_box()
                mp = small.locator("#music-visual-panel").bounding_box()
                assert md and mp and mp["x"] >= 0
                assert mp["x"]+mp["width"] <= 390 + 2, "music stage clipped on phone"
                assert mp["y"]+mp["height"] <= md["y"]+5, "stage overlaps mobile controls"
                small.screenshot(path=str(proof / "01-music-mobile.png"),full_page=False)
                small.locator("#music-visual-close").click()
                small.close()
                # Match the Architect's 876px desktop screenshot: check the
                # mid-width dock while music is off and the spectrum is opt-in.
                medium=context.new_page()
                medium.set_viewport_size({"width":876,"height":900})
                medium.goto(base,wait_until="domcontentloaded")
                medium.locator("#music-visual-toggle").click()
                assert medium.locator("#music-visual-panel").is_visible()
                middle_dock=medium.locator("#music-dock").bounding_box()
                middle_stage=medium.locator("#music-visual-panel").bounding_box()
                assert middle_dock and middle_stage
                assert middle_stage["width"]>=middle_dock["width"]*.80
                assert middle_stage["y"]+middle_stage["height"]<=middle_dock["y"]+5
                for cid in ("music-toggle","music-prev","music-play","music-next",
                            "music-select","music-version","music-visual-toggle"):
                    b=medium.locator("#"+cid).bounding_box()
                    assert b and b["x"]>=middle_dock["x"]-2 and (
                        b["x"]+b["width"]<=middle_dock["x"]+middle_dock["width"]+2), (
                        f"mid-width music control clipped: {cid}: {b}")
                assert "Conflux Marcellus" in medium.locator("h1").first.evaluate(
                    "(el)=>getComputedStyle(el).fontFamily")
                medium.screenshot(path=str(proof / "01-music-medium.png"),full_page=False)
                medium.close()
                page.screenshot(path=str(proof / "01-wayfinding-desktop.png"),full_page=True)
                observations.append("Four grouped nav areas, 15 unique room actions, visible Node responsibilities, reduced-motion and mobile navigation passed")


                # Personal theme journey: local preview, save, reload and
                # bounded manual agent proposal. Do not publish to Git in CI.
                page.locator('button[data-page="studio"]').click()
                page.locator("#studio h2").wait_for(state="visible")
                assert page.locator("#studio-colors input[type=color]").count() == 10
                page.locator("#studio-name").fill("Wayfarer CI")
                page.locator("#studio-advanced-colors summary").click()
                assert page.locator("#studio-color-violet").is_visible()
                page.locator("#studio-color-violet").fill("#a5b3c7")
                page.locator("#studio-advanced-colors summary").click()
                page.locator("#studio-save").click()
                page.wait_for_function(
                    "() => document.documentElement.style.getPropertyValue('--violet') === '#a5b3c7'")
                page.reload(wait_until="domcontentloaded")
                page.locator('button[data-page="studio"]').click()
                assert page.locator("#studio-color-violet").input_value() == "#a5b3c7"
                page.locator("#studio-texture").select_option("constellation")
                assert page.locator("body").get_attribute("data-texture") == "constellation"
                page.locator("#studio-save").click()
                page.reload(wait_until="domcontentloaded")
                page.locator('button[data-page="studio"]').click()
                assert page.locator("#studio-texture").input_value() == "constellation"
                # A complete four-color theme sits above the original
                # ten-color editor. All existing saved themes still load.
                assert page.locator("#studio-colors input[type=color]").count() == 10
                assert page.locator(".studio-harmony-grid input[type=color]").count() == 4
                assert page.locator("#studio-preset option").count() == 11  # ten presets + custom
                page.locator("#studio-preset").select_option("Sapphire Nocturne")
                assert page.locator("#studio-harmony-blue").input_value() == "#7ab8f9"
                assert page.locator("#studio-preset-preview .studio-preset-chip").count() == 4
                page.screenshot(path=str(proof / "01-palette-sapphire.png"), full_page=True)
                page.locator("#studio-texture").select_option("constellation")
                colored_sky = page.locator("body").evaluate(
                    "(e) => getComputedStyle(e).backgroundImage")
                page.locator("#studio-preset").select_option("Jade Aether")
                jade_sky = page.locator("body").evaluate(
                    "(e) => getComputedStyle(e).backgroundImage")
                assert colored_sky != jade_sky, "texture should react to different accent palettes"
                page.locator("#studio-texture").select_option("weave")
                assert page.locator("body").get_attribute("data-texture") == "weave"
                page.screenshot(path=str(proof / "01-palette-jade.png"), full_page=True)
                page.locator("#studio-link-complement").check()
                before_blue = page.locator("#studio-harmony-blue").input_value()
                page.locator("#studio-harmony-amber").fill("#f2ac62")
                after_blue = page.locator("#studio-harmony-blue").input_value()
                assert after_blue != before_blue, "blue should follow the changed gold hue"
                assert after_blue == page.locator("#studio-color-blue").input_value()
                assert page.locator("#studio-link-complement").is_checked()
                page.locator("#studio-harmony-blue").fill("#83c5ea")
                assert not page.locator("#studio-link-complement").is_checked(), (
                    "manual blue override must release the complement link")
                assert page.locator("#studio-color-blue").input_value() == "#83c5ea"
                page.screenshot(path=str(proof / "01-palette-harmony.png"), full_page=True)
                page.locator("#studio-save").click()
                page.reload(wait_until="domcontentloaded")
                page.locator('button[data-page="studio"]').click()
                assert page.locator("#studio-harmony-amber").input_value() == "#f2ac62"
                assert page.locator("#studio-harmony-blue").input_value() == "#83c5ea"
                assert page.locator("#studio-texture").input_value() == "weave"
                assert page.locator("#studio-preset").input_value() == "custom"
                observations.append("Ten curated palettes, four accent controls, complementary linking, texture color response and v1 persistence passed")
                # Codex renders in the panel; no nested external site or
                # login provider is contacted by this smoke test.
                page.route("**/api/codex/status", lambda route: route.fulfill(
                    status=200,content_type="application/json",
                    body=json.dumps({"installed":True,"running":False,"busy":False,
                                     "editing":False,"thread":None,"sequence":0})))
                page.route("**/api/codex/events?since=*", lambda route: route.fulfill(
                    status=200,content_type="application/json",
                    body=json.dumps({"events":[],"latest":0,"running":True,"busy":False,
                                     "editing":False,"thread":"thr_mock_1234"})))
                page.route("**/api/codex/start", lambda route: route.fulfill(
                    status=200,content_type="application/json",
                    body=json.dumps({"installed":True,"running":True,"authenticated":True,
                                     "editing":False,"busy":False,"thread":"thr_mock_1234",
                                     "account_type":"chatgpt","plan":"plus"})))
                observed_codex=[]
                def fake_codex_message(route):
                    packet=route.request.post_data_json
                    observed_codex.append(packet)
                    route.fulfill(status=200,content_type="application/json",
                        body=json.dumps({"accepted":True,"thread":"thr_mock_1234","editing":False}))
                page.route("**/api/codex/message",fake_codex_message)
                page.locator("#assistant-open-nav").click()
                assert page.locator("#assistant-dock").is_visible()
                assert page.locator("#assistant-dock select").count() == 0
                assert page.locator("#bridge-repository").is_hidden()
                page.locator("#codex-start").click()
                page.wait_for_function(
                    "() => document.querySelector('#codex-message')?.disabled === false",
                    timeout=10000)
                assert page.locator("#codex-message").is_enabled()
                page.locator("#codex-message").fill("Inspect Portal styles and report issues.")
                page.locator("#codex-send").click()
                page.get_by_text("Inspect Portal styles and report issues.",exact=True).wait_for(timeout=10000)
                page.wait_for_function("() => document.querySelector('#codex-transcript .codex-message.user') !== null")
                assert observed_codex and observed_codex[-1]["message"] == "Inspect Portal styles and report issues."
                assert page.locator("#codex-login").is_hidden()
                page.locator("#assistant-close").click()
                assert not page.locator("#assistant-dock").is_visible()
                page.locator('button[data-page="updates"]').click()
                assert page.locator("#development-setup").is_visible()
                assert page.locator("#updates-check").count() == 1
                assert page.locator("#updates-apply").count() == 1
                assert page.locator("#updates-relaunch").count() == 1
                assert page.locator("#pull-desk").count() == 1
                assert page.locator("#studio-commit").count() == 0
                assert page.locator("#bridge-chatgpt").get_attribute("href") == "https://chatgpt.com/"
                assert page.locator("#bridge-codex").get_attribute("href") == "https://chatgpt.com/codex/"
                page.locator("#bridge-repository").fill("wayfarer/CrystalCove")
                page.locator("#bridge-task").fill("Adjust Portal spacing and run tests.")
                page.locator("#bridge-save").click()
                assert page.locator("#bridge-open-prs").get_attribute("href") == "https://github.com/wayfarer/CrystalCove/pulls"
                assert "Adjust Portal spacing" in page.locator("#bridge-handoff").input_value()
                page.locator("#bridge-repository").fill("javascript:bad")
                page.locator("#bridge-save").click()
                assert page.locator("#bridge-status").get_attribute("data-error") == "true"
                page.locator("#bridge-repository").fill("wayfarer/CrystalCove")
                page.locator("#bridge-save").click()
                assert page.locator("#bridge-open-repo").get_attribute("href") == "https://github.com/wayfarer/CrystalCove"
                def fake_pr_list(route):
                    route.fulfill(status=200,content_type="application/json",
                        body=json.dumps({
                            "repository":"example/fork","connected":True,"truncated":False,
                            "pulls":[{"number":11,"title":"Theme tweak","draft":False}]
                        }))
                def fake_pr_detail(route):
                    route.fulfill(status=200,content_type="application/json",
                        body=json.dumps({
                            "number":11,"title":"Theme tweak","repository":"example/fork",
                            "head":"theme","base":"main","author":"Wayfarer",
                            "head_sha":"a"*40,"ticket":"reviewticket",
                            "mergeable":True,"mergeable_state":"clean","merge_available":True,
                            "review_complete":True,"partial_file_list":False,"body":"Compact padding",
                            "files":[{"filename":"theme_studio.css","status":"modified",
                                      "additions":1,"deletions":1,
                                      "patch":"@@ -1 +1 @@\\n-padding:12px\\n+padding:8px"}]
                        }))
                page.route("**/api/pulls/list",fake_pr_list)
                page.route("**/api/pulls/detail?number=11",fake_pr_detail)
                page.locator("#pull-refresh").click()
                page.locator("#pull-list").select_option("11")
                page.locator("#pull-inspect").click()
                page.locator("#pull-review").wait_for(state="visible",timeout=10000)
                assert "+padding:8px" in page.locator("#pull-files").inner_text()
                assert page.locator("#pull-merge").is_disabled()
                page.locator("#pull-reviewed").check()
                assert page.locator("#pull-merge").is_enabled()
                page.locator("#pull-reviewed").uncheck()
                assert page.locator("#pull-merge").is_disabled()
                page.unroute("**/api/pulls/list",fake_pr_list)
                page.unroute("**/api/pulls/detail?number=11",fake_pr_detail)
                page.screenshot(path=str(proof / "01-personal-studio.png"), full_page=True)
                observations.append("Embedded Codex chat and migrated external tools/fork handoff passed; original updater retained")

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
                columns = page.locator("#node-list").evaluate(
                    "(e) => getComputedStyle(e).gridTemplateColumns.split(' ').filter(Boolean).length")
                assert columns == 3, f"five cards should balance 3+2, got {columns} columns"
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

                page.locator('button[data-page="tour"]').click()
                page.locator("#video-tour-list .tour-card").first.wait_for(timeout=18000)
                assert page.locator("#video-tour-list .tour-card").count() == 4
                assert page.locator("#project-readme video").count() == 0
                page.screenshot(path=str(proof / "04-video-tour.png"), full_page=True)
                observations.append("Four optional tour clips live separately from the README; no automatic video playback")

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
                page.locator(".music-advanced summary").click()
                assert not page.locator(".music-advanced").evaluate("(e) => e.open"), (
                    "options should close before showing the wide spectrum")

                # Music On itself starts playback. Do not immediately click
                # Play a second time: it becomes Pause once audio is playing.
                page.locator("#music-toggle").click()
                page.wait_for_function("() => {const a=document.querySelector('#music-audio');return !a.paused && a.currentTime>0.8;}", timeout=18000)
                page.wait_for_timeout(1400)
                media = page.locator("#music-audio").evaluate(
                    "(e) => ({paused:e.paused,time:e.currentTime,ready:e.readyState,"
                    "source:e.currentSrc,error:e.error?.message || null})")
                assert media["time"] > 0.8 and not media["paused"], f"real MP3 playback failed: {media}"
                assert page.locator("#music-seek").is_enabled(), "seek must activate after metadata loads"
                assert page.locator("#music-duration").text_content() != "--:--", "song duration should display"
                page.locator("#music-seek").evaluate(
                    "(e) => {e.value='500'; e.dispatchEvent(new Event('input',{bubbles:true}));"
                    "e.dispatchEvent(new Event('change',{bubbles:true}));}")
                page.wait_for_function("() => document.querySelector('#music-audio').currentTime>20", timeout=15000)
                observations.append("Time display and scrubbing update the position in the real MP3")
                page.locator("#music-visual-toggle").click()
                assert page.locator("#music-visual-panel").is_visible()
                visual_state = page.locator("#music-visual-status").text_content()
                dock_box = page.locator("#music-dock").bounding_box()
                stage_box = page.locator("#music-visual-panel").bounding_box()
                canvas_box = page.locator("#music-spectrum").bounding_box()
                assert stage_box and dock_box and canvas_box
                assert stage_box["width"] >= dock_box["width"] * .78, (
                    f"soundstage needs to span the music dock: {stage_box} vs {dock_box}")
                assert canvas_box["width"] >= stage_box["width"] - 50, (
                    f"real spectrum canvas did not grow: {canvas_box}")
                assert stage_box["y"] + stage_box["height"] <= dock_box["y"] + 5, (
                    "wide soundstage should remain above the music controls")
                assert page.locator("#music-dock").evaluate(
                    "(e)=>getComputedStyle(e).display") == "grid"
                assert page.locator("#home .room-hero").evaluate(
                    "(e)=>getComputedStyle(e).boxShadow") != "none"
                assert page.locator("main > .notice").evaluate(
                    "(e)=>getComputedStyle(e).boxShadow") != "none"
                page.screenshot(path=str(proof / "05-music-while-exploring.png"), full_page=True)
                page.screenshot(path=str(proof / "05-wide-soundstage.png"), full_page=False)
                page.locator("#music-visual-close").click()
                assert not page.locator("#music-visual-panel").is_visible()
                observations.append("Optional spectrum panel opens and closes without starting or stopping music: " + visual_state)
                page.locator('button[data-page="home"]').click()
                assert not page.locator(".music-advanced").evaluate("(e) => e.open"), (
                    "music options should close when navigating to a new room")
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
