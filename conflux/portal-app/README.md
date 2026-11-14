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

**One-time setup:** Start the Portal normally from your cloned repository. In the new **Updates & Setup** room, click **Add to Applications Menu**. A user-local `Conflux Portal` entry is created for KDE and other compatible Linux desktop environments. No `sudo` is used. Search for **Conflux Portal** in your Linux application menu thereafter. It reuses the server only when it belongs to **that exact installed Portal checkout**. If an older ZIP copy or a different clone is already using `127.0.0.1:8765`, it reports the conflict instead of silently opening the wrong instance.

**Update sequence:**

1. **Check for Updates** contacts the official public CrystalCove **main** repository over HTTPS. It does not require an SSH key passphrase or update working files.
2. **Update** explicitly fast-forwards the checked commit. If you're previewing another branch, it first attempts a normal, safe switch to `main`. It will refuse branch divergence or changes that Git says would be overwritten.
3. **Relaunch** starts the freshly updated Portal on the same local port and refreshes the browser tab when the new server responds.

No step silently resets, stashes, cleans, rebases or forces your local working tree. Your existing `.obsidian` files and personal notes remain as-is; if Git detects a conflict, it stops and reports the reason rather than discarding work. A check is not an automatic update and a published commit is not an approval to deploy an external operating-system service. The buttons update the **cloned repository**, not the separately downloaded native Unreal game.

The updater requires a real Git checkout with a `main` branch and a verified `origin` pointing to `MedioCritasVT/CrystalCove` on GitHub (standard SSH and HTTPS forms are accepted). ZIP-only installations cannot self-update this way yet. The update fetch uses GitHub's public HTTPS address even if your normal Git remote uses SSH, avoiding noninteractive passphrase prompts. Git and a reachable GitHub connection are required.

For troubleshooting, **Updates & Setup** now shows the absolute path of the Portal checkout actually serving this browser tab. If you see the old ZIP folder, close that Portal process (Ctrl+C in the terminal where it was started), start `python3 portal.py` from your updated **Git clone's** `conflux/portal-app` folder, and refresh the browser with **Ctrl+Shift+R**. Do not force-close the browser or erase browser storage. Desktop-launched processes log to `~/.local/state/conflux-portal/portal.log`. Browser-local Atelier/Ledger data stays bound to `http://127.0.0.1:8765` for the same browser profile; keep backups.

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

## Ledger downloads — what each button does

The Ledger is a local-first record keeper, not a GitHub sync service. A committed entry is saved in your current browser's local storage at the Portal address.

- **Download readable Ledger (.md)** creates one file named `Conflux.md` containing **all committed entries** in a format you can open in Kate or another text editor. Approved records are in their own section, and the other statuses are preserved separately. It does **not** edit the original source files or automatically update itself.
- **Download restorable backup (.json)** creates `Conflux-ledger-backup.json` containing **all committed entries** as structured data you can restore into Ledger. Keep this backup somewhere safe.
- **Restore from backup** lets you select that JSON file and **asks for confirmation before replacing** the browser's current local Ledger entries. Back up current work before restoring.

Both download buttons create **point-in-time snapshots**, not continuously synchronized files. Commit new entries? Download fresh copies. These actions do not upload records to a server or to GitHub.

## Other ready applications

**Conflux Atelier (Medio/Nexus)** and **Conflux Ledger (Ratio/Limen)** are bundled original HTML apps. Their **Open** buttons work with no installation or executable registration. Export backups regularly, especially before clearing browser data or switching browsers.

The **Player Manual** renders the installed checkout's root **README.md** (served locally and refreshed after approved Git updates), followed by a separate gameplay quick reference. **Book 5** remains a labeled literary WIP with Chapters 3–10 currently in GitHub. **Concept Art** links to Ratio's labeled archive, not yet an approved final-asset gallery. The first expressive CSS chibi-style familiar previews are included; final reference-based character artwork remains pending. **VOS** remains disconnected and does not collect machine telemetry.

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

## Soundtrack (local-only preview)

The Portal has a global **Music Off / Music On** switch and a **Soundtrack** page. Music is **off by default** and never plays merely because you open the Portal or choose files. Its controls now live in a slim **bottom toolbar** on every page; expand **Music options** for file selection and ZIP import.

Click **Choose MP3s** to select locally saved audio recordings from your computer. The player builds a temporary in-browser playlist with previous/next, pause/play, volume, composition and alternate-version selection. Files named with suffixes such as `(2)`, `- v2`, or `- alternate` are grouped under one composition when the titles match. Selecting a different Portal page does not stop the player; switching it off pauses the audio. Browser audio permissions may require a fresh click on Play.

The `music.js` player uses the standard browser File API and local Blob URLs. **It does not upload or publish audio files.** Selected audio is released when the tab is closed/reloaded, so select files again next time. The public `conflux/soundtrack/catalog.json` is a **metadata-only working register**: eleven recordings across ten compositions, including both distinct `Sacrament of Oath` takes and the three later Architect-supplied tracks. All eleven are SHA-verified, including the three later Architect-supplied titles and Silicon Saints; none is confirmed published as a standalone MP3. The Architect confirms distribution eligibility; no mix is automatically declared final. The catalog holds proposed stable release filenames and full checksum verification in the soundtrack folder, but no audio binaries or streaming links are published yet.

**Distribution eligibility confirmed by the Architect (November 10, 2026), not independently audited.** The MP3 metadata identifies Suno-assisted generation, and six tracks have `mediocritasvt` artist metadata. The original seven source recordings have been staged for GitHub Release distribution with stable filenames and SHA-256 checksums; the release assets have not actually been uploaded yet. Visitors can currently select their own local music files to preview them in this player. Public streaming will be enabled only after exact uploaded audio links are verified. No general reuse license is conferred on visitors.

The musical catalog and player do not modify the existing Atelier, Ledger or native Unreal game packages.

## Soundtrack that appears automatically

The Conflux Soundtrack player is in the Portal on every page. **Music starts off** to respect browser autoplay rules. Visitors do **not** need to select individual tracks. When the public GitHub release `conflux-soundtrack-v0.1` contains the expected actual MP3 assets with their exact catalog filenames, the Portal discovers and loads the available titles from the official GitHub Release API on startup. Visitors simply press **Music On** (the browser requires a gesture to start audible playback). Track selection, two distinct **Sacrament of Oath** takes, volume and playback controls stay available across Portal rooms.

**Before the public release exists:** the Architect can install the prepared `Conflux_Soundtrack_Release_v0_1.zip` **once** using **Install soundtrack ZIP once…** in the player. The original seven-file archive or the newer **11-recording** `Conflux_Soundtrack_11_Recordings_Release_Ready.zip` can be imported into `~/.local/share/conflux-portal/soundtrack/` (or `$XDG_DATA_HOME/conflux-portal/soundtrack/`). The importer verifies the corresponding SHA-256 manifest, refuses incomplete or tampered sets, and keeps them for later offline listening. The Portal serves those verified local files from its loopback-only server on subsequent visits; no repeat import, MP3 selection, GitHub login or internet connection is necessary.

The ZIP is not streamed directly from GitHub: for browser streaming, publish **each MP3 individually** as a GitHub Release asset. The player and Soundtrack page offer **Download MP3** only for an asset whose exact name and official GitHub Release URL are confirmed by the public release API; no Git clone is required to obtain those assets. The verified ZIP installer accepts either the complete original seven-file edition or the complete eleven-file edition, checks each SHA-256 and refuses mixed/incomplete archives. A release ZIP alone is not enough for direct track playback. Uploaded files are not the same as licensing audio for unrelated third-party reuse.

**Still not implemented:** adding the new soundtrack recordings to the Unreal project, soundtrack scene placement, automatic looping/crossfade, selecting a final Sacrament take or unattended publishing. Streaming is conditional on actual GitHub release assets being present.


### ZIP picker error: source file cannot be read

If Firefox/KDE reports that the selected file lacks read permission, the Portal has **not** installed that file. The complete 11-track archive is approximately 55 MiB, below the 70 MiB limit, and its recording hashes have been checked. The file picker still needs read permission to the **actual copy you select**. Try a fresh download to a normal `~/Downloads/` folder rather than choosing a recently restored file from Trash. In Dolphin, check **Properties → Permissions** for your own account's read permission. Reopen the Portal's **Music options → Install soundtrack ZIP once…** and choose the readable copy. No `sudo`, archive extraction or code changes are required. If it still fails, record the exact Portal status error and your current browser/sandbox context; don't recursively chmod or change ownership of unrelated directories.

A new browser-side preflight reads the selected ZIP before sending it, so unreadable files show actionable guidance and make no install request. This cannot grant Firefox permissions it doesn't have. For a second check that the **correct** server is running, compare the checkout path under **Updates & Setup** with the Git folder you intended to launch.

## Safety and known limitations

The Portal listens on **127.0.0.1** only; **do not expose it through a proxy or public network**. POST actions require same-origin authorization and the server's per-session token. The native folder chooser is invoked only by clicking the button; there is no automatic home-directory scan, shell-command interpolation, or automatic execution of discovered applications. Even so, this is an **experimental local launcher, not a security-audited service**.

Local folder selection is supported only when `kdialog` or `zenity` is installed and accessible to the Python process; manual absolute-path search is the fallback. The finder does not automatically discover apps outside the chosen folder or inspect packed `.tar.gz` contents. There is no automatic game installer or background music service; repository updates require explicit action through Updates & Setup. Audio is discovered automatically from verified local installs or the public GitHub soundtrack release; the Portal never silently uploads music to GitHub.

Test locally using `python3 -m unittest test_portal.py -v`. The repository also has `.github/workflows/portal-smoke.yml` for non-destructive GitHub Actions validation; tests must pass before public release. These tests cover routes, app status, bounded scanning, symlink rejection, permission checks, explicit registration and JavaScript syntax. They do not substitute for a hands-on Linux desktop picker or full game-launch test.

**Governance:** proposal, test result, merge and deployment are distinct. The Architect retains review and approval authority.
