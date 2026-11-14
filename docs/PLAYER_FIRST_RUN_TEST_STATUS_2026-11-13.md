# Conflux player-first download and update test status

**Date:** 2026-11-13  
**Scope:** Public ZIP → Portal, standalone Linux game, and Git clone → Portal.  
**Evidence categories:** Architect-reported Bazzite walkthrough; verified main-branch source; local disposable-Git automated tests; outstanding real-machine validation.  
**Boundary:** No modification to the Architect's Bazzite installs, browser storage, private Sanctum, developer checkout or real native game is implied.

## Three artifacts, two principal audiences

| Artifact | Audience and purpose | Install/run | Update behavior on public main |
| --- | --- | --- | --- |
| GitHub **source ZIP** (`CrystalCove-main.zip`) | ZIP-first Portal newcomer | Extract; enter `conflux/portal-app`; run `python3 portal.py` (Python 3.10+) | **Not self-updatable** using current Git-only Portal updater. Download a new ZIP to a separate folder. |
| `git clone` of **CrystalCove** | Developer or player who wants repository versioning | Clone repository; run same local Python Portal | **Check → consented Update → Relaunch** can fast-forward the **whole official checkout** to public `main`, preserving unrelated local changes and refusing conflicts. |
| **Conflux-V0.1-Linux-x86_64.tar.gz** GitHub Release | Player who wants only the native game | Extract; run `PlayConflux.sh` with a compatible Vulkan driver | Independent game artifact. Git Portal updater **does not** replace it. |

**Not interchangeable:** GitHub's auto-generated source ZIP is neither a packaged game nor a supported one-click Portal installer. The local Python Portal, the static public website source and the standalone native Unreal game are separate entry points.

## Previously observed Bazzite ZIP route (reported, guided)

Source: [Approach-system walkthrough](APPROACH_SYSTEM_2026-11-12.md).

| Check | Status / evidence |
| --- | --- |
| Start in a fresh `~/Conflux` directory, leaving existing installs alone | **Reported passed** |
| Download GitHub source ZIP and extract `CrystalCove-main` | **Reported passed** |
| Find and start `conflux/portal-app/portal.py` | **Reported passed** using `python3 portal.py`; direct execute / Dolphin action yielded permission denied. **No sudo required.** |
| Open local Portal at `127.0.0.1:8765`, game not installed | **Reported passed** |
| Atelier save, reopen and Ledger `Hello World Test` commit/refresh/Inspect | **Reported passed** |
| Ledger readable Markdown download and same-data JSON backup restore | **Reported passed**; **not** proof of fresh-profile or cross-device recovery |
| Extract a later repository ZIP beside the old folder, reopen Portal | **Reported passed**; updated Ledger labels observed and previous browser entry remained |
| Press **Check for Updates** from a ZIP install | **Reported limitation:** HTTP 409, `Portal must run from its own CrystalCove Git clone.`; wording does not yet help a newcomer recover |
| Unassisted first-time discovery of downloads, fresh browser profile, game download/launch | **Not independently tested** |
| Fully automatic ZIP update, recovery and rollback on Bazzite | **Not shipped/verified**; proposed updater preview is not a public release |

The above is a **guided first-use and regression** history, not an unassisted new-player study. No guarantee about arbitrary user hardware follows from it.

## Git clone behavior: source audit and disposable tests

The current `conflux/portal-app/app_updater.py` validates a real checkout whose `origin` matches official `MedioCritasVT/CrystalCove`. A read-only check fetches `main` over HTTPS, compares ancestry and lists changed files. A **separately requested** apply performs `git switch main` (when needed) and `git merge --ff-only` of the checked commit. It has no code path to `reset --hard`, `git clean`, forced checkout, or silent stash. This operates at the repository root, therefore includes approved documentation, Portal code and tracked project records—not the separately downloaded native game.

Existing automated tests use disposable local Git repositories, with GitHub fetch overridden to a **local bare repository**. They cover an up-to-date check, unrelated modified Obsidian data, conflicting tracked changes, branch switching, origin restrictions, divergence and explicit prior approval.

**Additional tests proposed in the accompanying test branch:**
- Multi-area update of Portal code, `docs/` and `conflux/platforms/` in one consented fast-forward, preserving a private untracked file.
- Failed update check in a source ZIP extraction: no `.git`, no file changes; does **not** claim a functional ZIP updater.
- Unreachable remote: no file changes and no unchecked apply.

**Run locally in an isolated developer checkout:**

```bash
cd conflux/portal-app
python3 -m unittest test_app_updater.py -v
python3 -m unittest discover -p 'test_*.py' -v
node test_ui.js
```

These tests must pass in the [Portal smoke workflow](../.github/workflows/portal-smoke.yml) before treating the new cases as verified. Ubuntu CI is not a physical Bazzite/KDE or native Unreal-game test.

## Next player acceptance pass (pending)

1. **ZIP/Portal, first exposure:** With a disposable browser profile and new empty folder, follow root README without coaching; record exactly what is clicked and whether it is obvious that Portal does not require game or Git. Do not touch existing installations.
2. **ZIP/Portal, update:** Preserve an exported Ledger JSON backup, download a new source ZIP beside the old one, use the same browser/port, and confirm Atelier and Ledger still function. This is a **manual replacement**, not self-update. Verify restore only in a disposable profile.
3. **Clone/Portal:** Clone official `main` in a disposable folder and test check/current status, explicit apply after a new approved commit, a clean relaunch, and refusal when local conflicting files exist. Never run the updater on the Architect's working clone for a test.
4. **Native game/demo:** Independently extract the official `v0.1` release and locate `PlayConflux.sh`; check startup, profile creation, manual save and relaunch on actual supported Bazzite hardware. Keep this outcome distinct from Portal tests.
5. **Future player ZIP updater:** Before release, require an explicit consent prompt, verified source/version, safe extraction, staging, dirty-file protection, backup and rollback, restart and failure injection. The previous local universal-updater preview is **unverified** on a real ZIP install.

## Release and data boundaries

- **Do not** require Podman, Ollama, RabbitMQ, Unreal Editor, Tailscale, GitHub Pages, or a personal server for player Portal exploration.
- **Do not** overwrite a player's existing extraction, `~/.local/share/Conflux/V0.1/` game saves, or local Ledger records to make a test pass.
- Browser-local work is sensitive to profile + origin; export structured backups separately. An unchanged browser record after a ZIP extraction is useful evidence but is not a cross-machine migration proof.
- **No automatic permission** to update the user's own checkout, publish new audio/game assets, or deploy public/private server infrastructure is conferred by this test plan.
