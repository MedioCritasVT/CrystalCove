# Conflux Portal — Linux local preview 0.1

**Status: proposed development preview; NOT merged, deployed, production-tested or approved.** This application is separate from the static public GitHub Pages website proposed in PR #3.

## Run locally (Linux)

Requires Python 3.10+; uses only the standard library. Clone the repository, then:

```bash
cd CrystalCove/conflux/portal-app
python3 portal.py
```

Open the **exact loopback URL printed in the terminal**, e.g. `http://127.0.0.1:PORT`. The port is selected dynamically. Stop with Ctrl+C.

The UI works without VOS, Ollama, the game, GitHub credentials, or external services. External links to GitHub require internet.

## Configure explicit local application launch

**Do not copy commands from untrusted sources into this file.** Create `~/.config/conflux-portal/apps.json` with a list of approved local executable paths, for example:

```json
[
  {
    "id": "conflux-game",
    "name": "Conflux V0.1",
    "executable": "/absolute/path/to/extracted/Conflux/PlayConflux.sh"
  }
]
```

Replace the path with the actual executable path. The Portal never downloads, installs, searches the filesystem for programs, or starts applications automatically. The Launch button starts only the configured executable with no shell and no supplied arguments. Paths should point to software you trust; **configuring an executable grants it the same privileges as your Linux user**. Do not run this preview as root.

The local server listens on `127.0.0.1` only. The launch API requires a per-session token and same-origin POST request. It is a local development preview, **not a security-reviewed launcher**. Do not proxy or expose its port to a network or the public internet. Close the server when not in use.

## Implemented now

- Responsive, keyboard-accessible local navigation and blended Atelier/Ledger styling.
- First-run instructions, release links, manuscript/project navigation and persistent WIP disclosure.
- Explicitly configured local application discovery and opt-in launch.
- Honest VOS status: not connected; no false telemetry or automatic service startup.
- Five labeled Node placeholders. No fabricated reference-panel artwork.
- No login, remote accounts, media upload, telemetry collection or local data editing.

## Pending separate review

- Ratio's labeled, unique project-media upload, including concept art and development captures. Do not assume every image in the packaged game is separately reusable or cleared for public display.
- Actual reference-panel-based chibi art, optional interactions, and Node-specific submenu palettes.
- VOS service adapter with contract checks, opt-in access, stale/unknown/error reporting, and tests.
- App manifests, lifecycle supervision, Ledger/Atelier message contracts, and installation packages.
- Platform support beyond Linux.

## Validation checklist

1. On Linux, run `python3 portal.py`; verify the loopback URL opens.
2. Navigate all sections at desktop and mobile widths; verify focus and keyboard behavior.
3. With no `apps.json`, confirm no launch controls are available.
4. Configure one trusted executable, refresh, and test launch only with explicit consent.
5. Confirm VOS remains **not connected** when no VOS service is running.
6. Stop the server and confirm the interface becomes unavailable.
7. Independently review launcher safety and asset licensing before approving public use.

**Checkpoint 0.3 principle:** source, interpretation, approval and action remain separate. An app being visible does not mean it is trusted, running, or approved.
