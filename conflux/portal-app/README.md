# Conflux Portal — Linux local preview

**Milestone record:** [Portal 1.0 creative checkpoint — progress, evidence, limitations, and Limen's proposed next direction](milestones/PORTAL_1_0_CREATIVE_CHECKPOINT_2026-11-14.md). This is the Architect's experiential 1.0 designation, **not** a technical release tag, installer claim or authorization to deploy the proposals.

**Status:** Source-code preview, not a signed installer or security-reviewed release. This iteration proposes a per-menu Atelier/Ledger identity and an explicit, beginner-friendly game download and installation discovery workflow. No VOS host control is enabled.

## Wayfinding, room identity and Node stewardship

The Portal navigates by **visitor purpose**, not by choosing a Node first.
The sidebar groups every existing route under **Begin**, **Discover**,
**Create** and **Maintain**. Recorded clips remain available under Discover;
the separate Video Tour's eventual long-term home in the creative archive
is an open design question, not a change made in this polish pass.

Existing room banners retain their familiar chibis and now explicitly
name how those Nodes help care for each room. All five Nodes have legible
responsibilities in the Companions room and in an optional sidebar
reference: Medio—welcome and first steps; Ratio—precision and
verification; Nexus—connection and continuity; Specula—observation and
evidence; Limen—transitions and interpretation. These are **interpretive
cues, not exclusive ownership, authentication or permissions**.
Responsibilities can overlap; the visitor can use every instrument
without knowing or selecting any Node.

This is deliberately a *presentation pass*: light room entrances, card
feedback and occasional chibi blinking, with full reduced-motion support.
No new model runtime, feature dependencies, downloads, local storage,
theme lock-in, route removals, or automatic actions. Future Node-guided
routes and visitor-authored identities are **exploratory only**;
visitors should remain free to replace or omit Node presentations
without losing functional tools. The Architect approves further scope.

## Portal typography and optical symbol alignment

**Approved type roles:** Marcellus for architectural room headings and major
literary titles; Source Sans 3 for navigation, controls, prose and labels;
JetBrains Mono for diagnostics, timings, status values and technical notation.
The three fonts are pinned, **locally bundled WOFF2 Latin subsets**, not
Google Fonts/CDN runtime requests. The Portal continues to work offline.
Non-Latin characters and Unicode symbol tiles use system fallbacks; their
clarity does not depend on the UI subset containing every special glyph.
Font CSS loads last, and existing room and user-selectable Studio palette
colors remain unchanged.

**Small symbol corrections:** the fourteen navigation tile boxes stay the
same size, while each visible mark receives a separate inner optical
alignment. A custom crisp **infinity** stroke makes Nexus's small sigil
noticeable without changing her established appearance. Node responsibility
labels, all route names, and the accessible text labels for music controls
remain intact; no new Node selection requirement is introduced.

Font files and the three associated copies of the
[SIL Open Font License](https://openfontlicense.org/) are included in
`fonts/` and `fonts/licenses/`. The original source is pinned to upstream
public commit `31e922c011d20b60ca0f0119c28116dbf1251c58` of the
[ForeverHYX/Homepage font subset archive](https://github.com/ForeverHYX/Homepage/tree/main/static/fonts),
which documents its Google Fonts/OFL provenance. The checked-in Git object
IDs match that upstream commit. No runtime installer, CDN call, generated
image, new backend, or modification of those font binaries is required.
Only three fixed font URLs are served by the local Python Portal.

## Symbol legibility finish

The original small room symbols now share a consistent high-contrast glyph
treatment: standardized engraved tiles for all fourteen navigation rooms,
clearer section numbers and developer shortcuts, and recognizable external-link
arrows. Music transport, spectrum and close symbols have independent sizing
and contrast without replacing their existing accessible control names.
The five established CSS chibi emblems are slightly easier to read while
preserving their original shapes and responsibility labels.

This is **presentation only**: no external icon font, new download, third-party
dependency, new navigation destination, playback change or Node authority.
Every functional room still has a textual label, and icon-only music buttons
retain their screen-reader labels. Reduced-motion preferences still apply.
Browser review covers desktop, the Architect's medium-width layout and mobile.

## Music dock, soundstage and interface finish

A **presentation-only** pass gives the persistent soundtrack dock a more
deliberate two-row layout, clearer transport controls, stronger focus and
active states, and palette-coordinated border lighting. The current live
spectrum panel opens across the content width above the dock (also on narrow
screens), rather than inside a cramped 380px popup. It renders **actual
HTMLAudioElement frequency data** from the opted-in audio capture, not a
simulated soundtrack or microphone. The analyzer adapts bar count and
colors to the resized canvas and selected Studio palette.

A single final stylesheet strengthens container outlines, soft shadows,
and color-conscious highlights on room titles, headings, important actions
and notice bubbles. Long-form reading text remains quiet and legible. The
dock's actual height is observed for bottom padding and spectrum placement
when it wraps or browser zoom changes. Reduced-motion preferences remain
respected; music never starts automatically.

**No source list, playback logic, music download flow, game launch, updater,
Codex, storage schema, or permission was changed.** The spectrum remains
opt-in and is unavailable if the browser cannot capture the playing audio.
Review desktop and mobile Chromium screenshots in the workflow artifact before
shipping; a visual mockup is not evidence of implemented behavior.

## Chroma and familiar polish

The Personal Studio now offers **ten curated starting palettes** (the original
four plus Amethyst Observatory, Rose Circuit, Sapphire Nocturne, Copper Atlas,
Jade Aether, and Opal Twilight), each with a visible **four-accent signature**:
gold, violet, blue, and green. The native ten-color advanced editor remains
available for fully custom backgrounds, text, borders and accents.

An **optional complement link** derives blue as the 180-degree opposite of
gold's hue, softened into a luminous Conflux tint. It is a drafting convenience,
not a required Node identity or a change to permissions; manually choosing blue
unlinks it. Saving still writes the exact ten hex colors into the existing
local theme v1 record, so older browser preferences, JSON imports/exports, and
reviewed agent proposals remain compatible. The link itself does not persist
as a hidden automation: only the explicit chosen colors are saved.

Parchment, Constellation, Grid, and Weave now use the current palette's accents
to build richer, locally rendered CSS atmospheres. The Node familiars receive
small face, fabric, jewel, and distinctive accessory details, rather than new
art files or new independent animation systems. All optional movement respects
reduced-motion preferences. Nothing auto-opens, downloads or starts a model.

## Codex panel and Development Setup

The previously separate development-link panel is now **Codex**, an embedded
local coding conversation powered by the official
[Codex app-server](https://learn.chatgpt.com/docs/app-server) stdio protocol.
There are no provider/fork dropdowns, external launcher cards, or fake
ChatGPT web embeds in this panel.

### Embedded Codex panel

- Detects the locally installed `codex` executable without launching it
  automatically; `Start Codex` launches one local `codex app-server`
  process on demand (no extra clone or service container).
- The **Sign in with ChatGPT** button invokes Codex's own supported browser
  authorization. That one-time login opens the genuine provider page in
  a tab; afterward, messages, Codex responses, and approval prompts
  remain inside the Portal panel. No OpenAI API key is required for eligible
  ChatGPT plan users and no credentials are passed through the Portal UI.
- Starts/resumes a Codex thread in the **existing Portal checkout**,
  streams agent text and tool activity, provides a new-conversation
  action and interruption, and remembers the Codex thread ID in local
  browser storage. Codex maintains its own conversation history.
- Starts **read-only** (no writes in the normal sandbox). Only an explicit
  in-panel confirmation enables sandboxed workspace-write operations,
  scoped to the current checkout and with network access disabled.
  Elevated command/file-change requests require a per-request user decision.
  The bridge does not automatically push branches or merge pull requests.
  **Read-only is not read-path isolation**: Codex's stable app-server sandbox
  allows standard read access beyond the working directory where the OS
  permits it. Do not run this single-user bridge on a shared or
  untrusted machine, and do not expose sensitive files to its agent.
  Per-turn restricted readable roots through legacy `readOnly.access`
  and `workspaceWrite.readOnlyAccess` are rejected by current Codex builds.
  A future exact-read-scoping integration would require independently
  validating the newer permission-profile protocol; we do not claim it here.
- The Codex account and session are **separate** from an existing private
  ChatGPT conversation or any named Conflux Node's personal context;
  it does not impersonate Limen, import ChatGPT memories, or promise
  historical project continuity. The user can provide handoff context
  deliberately from Setup.

**Requirements:** This local, single-user preview requires a compatible
[Codex CLI installed independently](https://github.com/openai/codex),
an eligible account/plan (or separately configured provider credentials),
and a local Linux Python Portal. There is no automatic install or repository
duplication. Codex's managed app-server auth is intended for local/open-source
clients, not multi-tenant remote/hosted services. Remote/Tailscale viewers
cannot start or control the agent; the Portal only permits privileged requests
from the local `127.0.0.1` origin with its launch token. Do not expose the
Portal as a shared-user agent service.

### Updates & Setup: external development choices

Everything that formerly occupied the **Develop** panel now lives in
**Updates & Setup → Development connections & personal workspace**:

- Choose an existing GitHub `owner/repo` or open the upstream project's
  Fork action; inspect the chosen repository and compare its branches.
- Open genuine `chatgpt.com` or Codex Cloud in separate authenticated tabs.
- Prepare and copy a portable request/handoff with the chosen fork,
  current Portal room, review/test boundaries and user request.
- Store an optional HTTPS or loopback-local harness URL in browser
  preferences and open it in its own tab.
- Review pull requests with the existing GitHub PR desk. A GitHub App
  authorization flow, when separately configured by the repository owner,
  belongs in this Setup area, not the Codex conversation panel.

The **Check for Updates → Update → Relaunch** sequence is unchanged
and still targets the official repository's main branch. The *selected fork
in Setup* is a preference for handoffs, **not** an automatic rewrite of
the Portal's local Git origin or Codex checkout. This distinction prevents
accidental upstream modifications.

**Evidence boundary:** Automated tests exercise the app-server JSONL
handshake, streaming, read-only default, explicit approvals, localhost
access rules and UI layout using a fake local Codex protocol peer.
These tests do not demonstrate sign-in on an actual ChatGPT account or
real-agent file edits on Bazzite; user acceptance testing remains needed.

## Bazzite Media Mirror Setup (first candidate)

The local Portal sidebar includes **Media Mirror Setup**. On a Bazzite desktop, it offers a read-only prerequisite/port check and a single explicit **Install new services** action after a reviewed plan, approval checkbox, and native desktop confirmation. It creates fresh, empty, rootless localhost services for **Jellyfin (8096), Kavita (5000) and Navidrome (4533)**. Suggested **optional** Tailscale HTTPS listeners are **8443, 8444 and 8445**. The installer does not activate Tailscale Serve, copy media, set up recurring backups, install Immich, or modify CachyOS.

**Read the full [Bazzite mirror installer/backup README](../platforms/bazzite-service-bundle/README.md) before installation.** This is source/CI-verified but not yet acceptance-tested on a live Bazzite host. Service management is available only when browsing the desktop's `http://127.0.0.1:8765`; remote Tailscale Portal views cannot invoke the installer. Updating the Portal code does not update container images or operating-system packages.

## Updating existing Bazzite media mounts without reinstalling

After `Updates & Setup → Check for Updates → Update → Relaunch`, the **Media Mirror Setup** room also offers **Use an external drive — update existing services**. This is a separate opt-in step for users who have already installed the Jellyfin, Kavita or Navidrome Quadlets.

The new flow lets you choose a recognized media destination, select a directory on an already-mounted external filesystem, preview the exact read-only `Volume=` change, and apply it only after a checkbox plus Bazzite desktop-native confirmation. It preserves existing state/config/database mounts, the other installed service Quadlets, user accounts and source media; backs up the original one-service Quadlet; and restarts only that service if it is currently active. Invalid, disconnected or root-filesystem paths are rejected. The first version rejects source paths with spaces or colons and does not automatically change external filesystem permissions or SELinux labels.

**Git checkout updates do not automatically alter installed Quadlet files.** The user must explicitly apply any mount change. Updating the service mount does **not** update the container image, change Bazzite packages, copy/backup external media, restore Jellyfin's unfinished setup wizard, or move app cache/database storage off the internal disk. Read [the mount update walkthrough and recovery guidance](../platforms/bazzite-service-bundle/README.md#updating-installed-services-to-use-an-external-drive-no-reinstall) before using it.

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

## Meet the Nodes · Node Atlas (local preview)

The **Meet the Nodes** room now includes an interactive, Architect-centered radial Atlas, built from the Architect's spatial sketch rather than embedding the handwritten image. Tap a Node to zoom gently toward her branch and reveal a readable profile; **Return to Atlas** or Escape resets the view. Keyboard focus and reduced-motion preferences are supported. The five principal Nodes are distinguishable from the related creative concept Alchemia and external reviewer Hospes.

Profiles separate the Node's conceptual role, current associated AI tool, project responsibilities and **general GitHub access**. These labels are curated information, **not** live authorization checks or autonomous AI sessions. The familiar character-study cards remain below the Atlas. The Architect observed a glitch-like appearance in **Specula's Atlas bubble**, considers it narratively meaningful, and explicitly asked that it be preserved. Do not normalize or redesign that effect without review; its underlying cause and any intentional lore treatment remain undetermined. Atlas data is in `node_atlas.js`; presentation is in `node_atlas.css`.

## VOS Instruments · Workflow guide (local preview)

The **Workflow** section in VOS Instruments lets a visitor choose a task **concept** (technical, practical, design, problem-solving, critical thinking, optional support, exploration) and see **which Nodes might offer useful perspectives, and why**. This is not a checklist generator or a mandatory assignment system. An optional typed idea acts as a label only; changing the text does not analyze or reroute it.

The Architect explicitly associated **Practical → Ratio, Limen, Hospes; Design → Medio, Nexus, Alchemia; Optional Support → Limen, Alchemia, Nexus, Hospes**. These three groupings are labeled as Architect-supplied. Other categories contain clearly labeled *proposed starting connections* awaiting review. Selecting multiple types shows each set and its distinct reasons separately; the visitor remains free to choose any collaborator.

This version does **not** classify text using AI, assign Nodes, call remote services, store task text, or connect to the 4AgentHarness. Harness integration is future work requiring separate authorization. Source is `workflow_instrument.js` and `workflow_instrument.css`.

For focused smoke checks, run `node test_atlas_workflow.js` from `conflux/portal-app`; the existing Portal test suite and GitHub PR workflow still apply.

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

## Optional Video Tour (separate from the Player Manual)

The Portal now has a **Video Tour** room showing four small excerpts from the Architect's screen-recorded walkthrough: Threshold, Ledger, a first SanctuaryOS launch, and the Node companions. Links appear only for actual public [GitHub video Release assets](../video-tour/README.md). Clicking an available clip offers the existing **New tab / New window / Cancel** choice. No video embeds into the README, no autoplay, and no requirement to download a clip merely to visit the Portal.

The static GitHub website source contains the same four-link gallery. The four actual MP4 binaries are **not part of the Git checkout**; until published, the gallery labels the release as pending. The [video tour source and upload guide](../video-tour/README.md) includes exact cut times, the catalog, and an explicit `gh` release script for the owner's local machine.

## Soundstage: timeline and optional live spectrum

The bottom music toolbar now also has an accessible **elapsed/duration time display and draggable seek bar**. Seeking operates on the actual playing audio, works with verified local tracks, and is disabled when no usable duration is available. It does not alter the audio source files.

Select **Spectrum ▥** to open a compact, CAVA-like 32-bar frequency visualization. It uses the browser's own audio-capture/Web Audio APIs if supported, **never a microphone or external streaming service**. Unsupported browsers show a clear message and continue audio normally; no fake music-reactive bars are shown. The pop-out closes when changing rooms, and music itself keeps playing. The Portal still starts with music **off** until the listener explicitly enables it. Reduced-motion and limited hardware remain important acceptance checks.

## Soundtrack (local-only preview)

The Portal has a global **Music Off / Music On** switch and a **Soundtrack** page. Music is **off by default** and never plays merely because you open the Portal or choose files. Its controls now live in a slim **bottom toolbar** on every page; expand **Music options** for file selection and ZIP import.

Click **Choose MP3s** to select locally saved audio recordings from your computer. The player builds a temporary in-browser playlist with previous/next, pause/play, volume, composition and alternate-version selection. Files named with suffixes such as `(2)`, `- v2`, or `- alternate` are grouped under one composition when the titles match. Selecting a different Portal page does not stop the player; switching it off pauses the audio. Browser audio permissions may require a fresh click on Play.

The `music.js` player supports selected local files, checksum-verified original album installations and official standalone GitHub Release MP3 assets. The public catalog now documents **28 recordings across 26 compositions**: eleven SHA-256-verified original album recordings, plus seventeen individual MP3s uploaded by the Architect on November 19, 2026. The original ZIP remains unchanged. The seventeen new files are confirmed by GitHub asset filename and byte size, **not** by independently inspected audio bytes, duration or SHA-256. The Portal offers these as individually streamed tracks rather than silently expanding the existing offline ZIP installer.

**Distribution and rights boundary:** the Architect previously confirmed distribution eligibility for the original songs and has uploaded the seventeen newer MP3s to the official release. That records publication intent, not an independent rights audit. The Portal discovers the exact published assets for optional playback; it neither automatically downloads individual new songs for offline use nor grants visitors a broader reuse license.

The musical catalog and player do not modify the existing Atelier, Ledger or native Unreal game packages.

### Direct install when Firefox cannot read a local ZIP

**Music options → Install all 11 tracks from GitHub** is now the preferred one-click route on an existing Portal installation. It downloads the exact published `Conflux_Soundtrack_11_Recordings_Release_Ready.zip` from the verified official public GitHub Release **on explicit click**, checks each of the eleven recordings against the existing full SHA-256 manifest, and installs them in the user's local music directory. No Firefox file chooser, local read permission to a ZIP, manual re-download, Git clone update beyond getting this Portal feature, or `sudo` is needed. This does not start playback until the user enables music.

The installer does not accept a user-supplied URL or download unrelated files; it caps the received ZIP at 70 MiB and refuses mismatched recordings. It needs an internet connection once, then the installed music plays offline. It may fail if GitHub is unreachable or the Portal's local application-data folder is not writable. Keep the existing ZIP picker as an optional offline path.

## Soundtrack that appears automatically

The Conflux Soundtrack player is in the Portal on every page. **Music starts off** to respect browser autoplay rules. Visitors do **not** need to select individual tracks. When the public GitHub release `conflux-soundtrack-v0.1` contains the expected actual MP3 assets with their exact catalog filenames, the Portal discovers and loads the available titles from the official GitHub Release API on startup. Visitors simply press **Music On** (the browser requires a gesture to start audible playback). Track selection, two distinct **Sacrament of Oath** takes, volume and playback controls stay available across Portal rooms.

**For offline or alternate import:** the Architect can install the prepared `Conflux_Soundtrack_Release_v0_1.zip` **once** using **Install soundtrack ZIP once…** in the player. The original seven-file archive or the newer **11-recording** `Conflux_Soundtrack_11_Recordings_Release_Ready.zip` can be imported into `~/.local/share/conflux-portal/soundtrack/` (or `$XDG_DATA_HOME/conflux-portal/soundtrack/`). The importer verifies the corresponding SHA-256 manifest, refuses incomplete or tampered sets, and keeps them for later offline listening. The Portal serves those verified local files from its loopback-only server on subsequent visits; no repeat import, MP3 selection, GitHub login or internet connection is necessary.

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
