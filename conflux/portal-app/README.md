# Conflux Portal — Linux local preview 0.1

**Status: development preview.** The initial Portal scaffold reached `main` through PR #4, but the later bundled-app fixes and verification work remain on `app/portal-linux-preview-0-1` pending review. The static public entry page is a separate `docs/` implementation. This is not yet a polished one-click installer or a security-reviewed launcher.

## Start on Linux

Requires Python 3.10+ (standard library only). From the **repository root**, use:

```bash
git fetch origin
git switch app/portal-linux-preview-0-1
git pull --ff-only
cd conflux/portal-app
python3 -m unittest test_portal.py -v
python3 portal.py
```

If you are **already** in `conflux/portal-app`, do not `cd` into it again. Run the last two Python commands from your current directory. Open the exact `http://127.0.0.1:PORT` address printed by Python. By default the Portal stays at **http://127.0.0.1:8765** across restarts so Atelier/Ledger browser storage stays visible. Stop the server with Ctrl+C. If port 8765 is already in use, close the previous Portal process; you can choose another *stable* port by setting `CONFLUX_PORTAL_PORT` before running Python.

The Portal itself works without the game, VOS, Ollama, a GitHub login, or external services. Links to GitHub require internet access. Don't use a `file://` URL for `index.html`; that bypasses the Portal service.

## What is available

- **Game V0.1:** Download opens the published GitHub release. If you register its installed executable in the local configuration, that same entry becomes **Launch**.
- **Atelier (Medio/Nexus):** The original standalone HTML application is bundled in `apps/atelier.html`, and **Open** loads it in a browser tab. Its navigation is local; no executable path is needed.
- **Ledger (Ratio/Limen):** The original standalone HTML application is bundled in `apps/ledger.html`, and **Open** loads it similarly.
- **Player Manual:** The Portal's section contains actual game controls, exploration and saving instructions, not GitHub setup. `PLAYER_MANUAL.md` is the portable gameplay guide.
- **Book V:** The Library points to the WIP manuscript directory with currently published Act I Chapters 3–10. Chapters 1–2 are not present as full manuscript files.
- **Concept art:** Ratio published a labeled concept-art archive and media release on `main`. The Portal links to this archive; a curated interactive gallery and chibi companions remain pending.
- **VOS:** Not connected; no real machine telemetry or VOS service is started.

## Optional game launch configuration

Create `~/.config/conflux-portal/apps.json` with a local executable you trust:

```json
[
  {
    "id": "conflux-game",
    "name": "Conflux V0.1",
    "executable": "/absolute/path/to/extracted/Conflux/PlayConflux.sh"
  }
]
```

Replace the path with the location on your machine, and ensure the script is executable. The app ID must be exactly `conflux-game`. **Downloading the archive does not automatically install or register it.** The Portal does not search your system or launch anything until you explicitly click Launch. Registered executables run with your normal Linux user permissions. Do not run this app as root.

## Tests and limits

Run `python3 -m unittest test_portal.py -v` from `conflux/portal-app`. This tests local routes, bundled file availability, download/open/launch status decisions, and that unauthorized launch requests are refused; if Node.js is installed, it also syntax-checks the Portal JavaScript. It does **not** execute any external app. Review any failing check before trying Launch.

The server binds only to `127.0.0.1`. It uses an origin check and token for launch requests, but has **not** had an external security audit. Do not expose it to the network. Original Atelier/Ledger browser data is associated with the local browser profile and origin; use their export/backup controls before clearing browser data. Changing the local port, using a different browser/profile or clearing site data changes which browser storage is visible. Keep the default port stable, and export backups regularly. If an earlier preview ran on a random port, its old work will not automatically migrate to 8765. Cross-browser persistence is not verified.

This preview is not yet a proper Linux package, automatic app installer, release-feed updater, actual VOS integration, or full offline book gallery. Those are separate future steps requiring design review and testing.

**Approval boundary:** Archived material, working code, tests, published releases, architectural proposals and production approval are different statuses. No upload or commit authorizes deployment to the Architect's host.
