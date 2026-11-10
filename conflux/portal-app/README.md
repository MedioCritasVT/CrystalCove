# Conflux Portal — Linux local preview

**Status:** Source-code preview, not a signed installer or security-reviewed release. This iteration proposes a per-menu Atelier/Ledger identity and an explicit, beginner-friendly game download and installation discovery workflow. No VOS host control is enabled.

## Run locally

Python 3.10 or later is required. From the cloned **CrystalCove repository root**:

```bash
cd conflux/portal-app
python3 -m unittest discover -p 'test_*.py' -v
python3 portal.py
```

If you are already in `conflux/portal-app`, skip the `cd` command. Open `http://127.0.0.1:8765`. Keep the port stable: the bundled Atelier and Ledger each use browser-local storage, which is specific to your browser profile and the exact origin (including port).

## No-terminal updates and desktop access (new preview)

**One-time setup:** Start the Portal normally from your cloned repository. In the new **Updates & Setup** room, click **Add to Applications Menu**. A user-local `Conflux Portal` entry is created for KDE and other compatible Linux desktop environments. No `sudo` is used. Search for **Conflux Portal** in your Linux application menu thereafter. It opens your already-running instance if present, or starts it on `127.0.0.1:8765` and opens your default browser.

**Update sequence:**

1. **Check for Updates** contacts the official public CrystalCove **main** repository over HTTPS. It does not require an SSH key passphrase or update working files.
2. **Update** explicitly fast-forwards the checked commit. If you're previewing another branch, it first attempts a normal, safe switch to `main`. It will refuse branch divergence or changes that Git says would be overwritten.
3. **Relaunch** starts the freshly updated Portal on the same local port and refreshes the browser tab when the new server responds.

No step silently resets, stashes, cleans, rebases or forces your local working tree. Your existing `.obsidian` files and personal notes remain as-is; if Git detects a conflict, it stops and reports the reason rather than discarding work. A check is not an automatic update and a published commit is not an approval to deploy an external operating-system service. The buttons update the **cloned repository**, not the separately downloaded native Unreal game.

The updater requires a real Git checkout with a `main` branch and a verified `origin` pointing to `MedioCritasVT/CrystalCove` on GitHub (standard SSH and HTTPS forms are accepted). ZIP-only installations cannot self-update this way yet. The update fetch uses GitHub's public HTTPS address even if your normal Git remote uses SSH, avoiding noninteractive passphrase prompts. Git and a reachable GitHub connection are required.

For troubleshooting, desktop-launched processes write a local log under `~/.local/state/conflux-portal/portal.log`. Browser-local Atelier/Ledger data stays bound to `http://127.0.0.1:8765` when you use the same browser profile. Keep exports/backups of important workspace content.

## Start playing

1. Choose **Get the Game** from the Portal, or **Applications → Download** for Conflux V0.1.
2. The local **Get Conflux V0.1** page has separate, verified GitHub links for the playable [Linux archive](https://github.com/MedioCritasVT/CrystalCove/releases/download/v0.1/Conflux-V0.1-Linux-x86_64.tar.gz), [release page](https://github.com/MedioCritasVT/CrystalCove/releases/tag/v0.1), [checksum](https://github.com/MedioCritasVT/CrystalCove/releases/download/v0.1/SHA256SUMS), and developer source archive. Do not confuse the native source archive or GitHub's repository ZIP with a runnable game.
3. Download and extract the Linux archive (about 1.18 GB compressed and 3.2 GB extracted). Do **not** select the `.tar.gz` file in the finder: it needs an **extracted folder**.
4. In **Already cloned or downloaded?**, click **Choose game folder…**. On Linux systems with `kdialog` (KDE) or `zenity`, a native desktop picker opens. On systems without either, paste an absolute folder path copied from your file manager and choose **Search this folder**.
5. The Portal searches **only that selected folder and up to four nested levels**, capped at 450 directories, for `PlayConflux.sh`. It will show its path; click **Use this game** to explicitly register it.
6. The primary game button becomes **Launch**, without downloading anything again. The game does not launch while you browse or register.

**A source-code clone is not automatically an installed game.** If you have only cloned the CrystalCove repository, the finder may report no `PlayConflux.sh`; download the packaged Linux release instead. If the script exists but is not executable, use your file manager's permissions controls to permit execution, then search again. Only run a build you trust.

For advanced users, manual registration via `~/.config/conflux-portal/apps.json` still works:

```json
[
  {
    "id": "conflux-game",
    "name": "Conflux V0.1",
    "executable": "/absolute/path/to/extracted/game/PlayConflux.sh"
  }
]
```

The folder finder writes the game entry to that file, preserves any unrelated entries, and creates new configuration files with user-only permissions. An invalid existing config is never silently overwritten.

## Other ready applications

**Conflux Atelier (Medio/Nexus)** and **Conflux Ledger (Ratio/Limen)** are bundled original HTML apps. Their **Open** buttons work with no installation or executable registration. Export backups regularly, especially before clearing browser data or switching browsers.

The **Player Manual** contains actual gameplay guidance. **Book 5** remains a labeled literary WIP with Chapters 3–10 currently in GitHub. **Concept Art** links to Ratio's labeled archive, not yet an approved final-asset gallery. Node character/pet illustrations remain pending. **VOS** remains disconnected and does not collect machine telemetry.

## Room identity and companions

Color is not limited to the navigation. The **entire page atmosphere** changes between rooms: a room-specific background gradient, headline and lead typography, card surfaces, text accents, and little symbolic Node familiars beside the heading.

The room palettes are derived from the original Atelier (Medio amber `#e9bf84` and Nexus violet `#c2a4f3`) and Ledger (Ratio blue `#84bff3` and Limen green `#9cdec0`). Specula is expressed through an additional cooler silver-blue observational motif. Menu buttons remain mostly neutral so the room itself, not the toolbar, carries the atmosphere.

| Room | Companion assignment | Room feeling |
| --- | --- | --- |
| Threshold | Medio + Nexus | Welcoming amber/violet sanctuary |
| Applications | Nexus + Ratio | Violet with lucid blue-green workbench tones |
| Get the Game | Ratio + Medio | Precise blue with warm introductory amber |
| VOS Instruments | Specula + Limen | Clear silver-blue observation and careful green thresholds |
| Library & Art | Nexus + Specula | Violet archival atmosphere, warm margins, provenance |
| Node Companions | All five | Shared space with five distinct identities |
| Player Manual | Medio + Limen | Gentle amber/green first-steps guidance |

The little CSS-drawn familiars are **new, provisional interface motifs**, deliberately labeled as such; they are **not the final chibi character designs**, not copies of the reference sheets, and not claims that any AI Node is running or independently acting inside the Portal. The character sheets and Ratio's media catalog remain in the project archive, pending a separate visual-art review before replacing them.

The UI test `node test_ui.js` checks every room's companion slot, assigned pet count, distinct page atmospheres, functioning navigation, and the existing download/launch flow. This supplements `python3 -m unittest test_portal.py -v`. Both are run by the PR GitHub workflow.

## Safety and known limitations

The Portal listens on **127.0.0.1** only; **do not expose it through a proxy or public network**. POST actions require same-origin authorization and the server's per-session token. The native folder chooser is invoked only by clicking the button; there is no automatic home-directory scan, shell-command interpolation, or automatic execution of discovered applications. Even so, this is an **experimental local launcher, not a security-audited service**.

Local folder selection is supported only when `kdialog` or `zenity` is installed and accessible to the Python process; manual absolute-path search is the fallback. The finder does not automatically discover apps outside the chosen folder or inspect packed `.tar.gz` contents. There is no auto-installer, auto-updater, background agent or automatic synchronization with GitHub yet.

Test locally using `python3 -m unittest test_portal.py -v`. The repository also has `.github/workflows/portal-smoke.yml` for non-destructive GitHub Actions validation; tests must pass before public release. These tests cover routes, app status, bounded scanning, symlink rejection, permission checks, explicit registration and JavaScript syntax. They do not substitute for a hands-on Linux desktop picker or full game-launch test.

**Governance:** proposal, test result, merge and deployment are distinct. The Architect retains review and approval authority.
