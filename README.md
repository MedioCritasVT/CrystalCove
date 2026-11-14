# Conflux / CrystalCove

> **Potential is the reason; possibility is the goal.**

### An inhabitable world. An experimental computing environment. An unfinished undertaking.

Conflux combines a fantasy game, original stories and music, creative tools, and experiments in human–AI collaboration. Its world begins in **Sanctuary Reach**, a harbor city beneath Yggdrasil, where five Nodes bring different perspectives to the realms and the work around them.

**Conflux** is the wider creative project; **SanctuaryOS** is the inhabitable game world; **VOS (Virtual Operational Space)** is a proposed independent software and service foundation. Fictional roles, AI collaboration, and real technical permissions are distinct. The goal is computing that people can question, understand and help shape—not a claim that the current prototypes already achieve it.

The native game, local Portal, books, music and development records are at different stages of completion. **This is a work in project.** You can enter as a player, reader, listener, creator or developer without adopting every part of the project.

*The answers show, but do you see?*

## Watch Conflux before you download — four short clips

The Portal is a welcome, not an installation requirement. If you're curious about what awaits, these **four short videos** open directly from GitHub Releases. No game installation, Git clone, or GitHub account is needed.

| A glimpse of… | Watch | Duration |
| --- | --- | ---: |
| **Threshold — A Place to Begin** | [Watch the welcome](https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-portal-tour-v0.1/01-threshold-welcome.mp4) | 13 seconds |
| **Ledger — Keeping the Record** | [Watch the workspace](https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-portal-tour-v0.1/02-ledger-workspace.mp4) | 13 seconds |
| **SanctuaryOS — First Launch** | [Watch the playable preview](https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-portal-tour-v0.1/03-game-first-launch.mp4) | 16 seconds |
| **Meet the Node Familiars** | [Watch the chibis](https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-portal-tour-v0.1/04-node-companions.mp4) | 11 seconds |

These are excerpts of an early Portal walkthrough, not a finished-game demonstration. You can also [browse all four on their GitHub Release page](https://github.com/MedioCritasVT/CrystalCove/releases/tag/conflux-portal-tour-v0.1). The Portal and public website offer a separate **Video Tour**; the Player Manual remains text-first, without embedded autoplaying videos.

## Start here — choose your experience

**The Portal is the intended welcome. The game is optional.** These are different downloads; a GitHub repository ZIP is **not** the playable Unreal game archive.

| I want to… | Start with | What I need |
| --- | --- | --- |
| **Explore the Portal as a player** | [First-time ZIP walkthrough](docs/FIRST_TIME_SETUP.md) · [Download repository ZIP](https://github.com/MedioCritasVT/CrystalCove/archive/refs/heads/main.zip) | Linux, Python 3.10+, browser; **no Git required** |
| **Keep an updatable project checkout** | [Git clone walkthrough](docs/FIRST_TIME_SETUP.md) · [Portal setup and update details](conflux/portal-app/README.md) | Linux, Python 3.10+, Git |
| **Play only the game/demo** | [Conflux V0.1 Linux release](https://github.com/MedioCritasVT/CrystalCove/releases/tag/v0.1) | Linux x86_64 and compatible Vulkan graphics; **no Portal or Git required** |

### Player route: repository ZIP → local Portal

1. Download the **repository ZIP** above (or **Code → Download ZIP** on GitHub) and extract it into a **new** folder. Do not overwrite an existing installation.
2. In the extracted `CrystalCove-main/conflux/portal-app` folder, open a terminal and run `python3 portal.py`.
3. Visit `http://127.0.0.1:8765`. Explore Atelier, Ledger, the Player Manual or other rooms. **Get the Game** is optional.

This is currently a Python-based local preview, **not** a one-click player installer. The repository ZIP does not include the runnable game, and the Portal's existing Git updater does **not** update ZIP extractions. Until a separately tested ZIP updater ships, download newer repository ZIPs into separate folders and keep the old copy until verified.

### Developer/updatable route: Git clone → local Portal

From an empty destination on Linux:

```bash
mkdir -p "$HOME/Conflux"
cd "$HOME/Conflux"
git clone https://github.com/MedioCritasVT/CrystalCove.git CrystalCove
cd CrystalCove/conflux/portal-app
python3 portal.py
```

Open `http://127.0.0.1:8765`. In **Updates & Setup**, choose **Check for Updates → Update → Relaunch**. For a verified official Git clone, this can fast-forward the **whole CrystalCove checkout** to public `main`, not just the Portal directory. Checking is not installing; an update requires a separate action. It refuses divergent history and local changes that Git cannot safely preserve; no reset, stash, clean or force is used. Switching from another branch to `main` may be offered explicitly. This does **not** update the separately installed native Unreal game.

**Keep your work safe:** Portal Atelier/Ledger work is stored in the browser profile under its local address and port, while game saves live separately. Before replacing an installation or changing browsers, export Ledger's **Download restorable backup (.json)** and any other important workspace data. A Markdown Ledger download is a readable snapshot, **not** a restore backup. Keep the same browser profile and `127.0.0.1:8765` address when reopening, but do not treat browser storage as a backup.

More detail: [Bazzite/KDE first-use guide](docs/FIRST_TIME_SETUP.md) · [Portal operation, limitations and troubleshooting](conflux/portal-app/README.md) · [Approach-system observations](docs/APPROACH_SYSTEM_2026-11-12.md) · [Current ZIP/Git/game test status](docs/PLAYER_FIRST_RUN_TEST_STATUS_2026-11-13.md).

## Play the standalone Conflux V0.1 Linux preview

**[Download the runnable Linux x86_64 game archive](https://github.com/MedioCritasVT/CrystalCove/releases/download/v0.1/Conflux-V0.1-Linux-x86_64.tar.gz)** (about **1.18 GB** compressed, **3.2 GB** extracted).

1. Download and **extract** the archive, then find `PlayConflux.sh` inside the extracted game folder.
2. Run `./PlayConflux.sh` in a terminal opened in that folder. If it says *Permission denied*, inspect that script's executable permissions; do not use `sudo` to launch the game.
3. Choose **Begin a new journey** and save your progress manually.

The release is a development preview, tested on the Architect's Bazzite/NVIDIA system, not certified for all Linux distributions or GPUs. It needs Vulkan support for the current SM6 renderer; first use may briefly hitch. No Windows/macOS build is supplied in V0.1. You do **not** need Unreal Editor or an account to play.

Explore the connected city and harbor, Yggdrasil, surrounding travel locations, Node realm presentations, the Unwritten avatar, Duskwing Grotto encounters, crafting, the Sapphire Grimoire, photo mode and creative systems. Parts of the combat, animation, story and realm progression remain unfinished. This is not a full campaign release.

**Controls:** WASD move · right-mouse drag look · mouse wheel zoom · E interact · Shift sprint/hover · Escape/menu settings and manual save. Journey progress **does not automatically save on quit**. Default save path: `~/.local/share/Conflux/V0.1/` (or under `XDG_DATA_HOME`). See the Portal's **Player Manual** for the gameplay-first introduction.

### Downloads are not interchangeable

- **Runnable game:** [Conflux-V0.1-Linux-x86_64.tar.gz](https://github.com/MedioCritasVT/CrystalCove/releases/download/v0.1/Conflux-V0.1-Linux-x86_64.tar.gz) — extract and play.
- **Native Unreal source inputs:** [Conflux-V0.1-Source.tar.gz](https://github.com/MedioCritasVT/CrystalCove/releases/download/v0.1/Conflux-V0.1-Source.tar.gz) — rebuilding needs Unreal Engine 5.8.4, which is **not** included.
- **GitHub source ZIP / clone:** project records, Portal Python code and historical sources, **not** the standalone cooked Unreal game.
- **Verification:** [Release assets and SHA256SUMS](https://github.com/MedioCritasVT/CrystalCove/releases/tag/v0.1) · [Build record](conflux/releases/v0.1/README.md) · [Build fingerprints](conflux/releases/v0.1/BUILD.json).

The build/package and bounded save checks passed; complete campaign coverage, every hardware configuration and final artistic acceptance have **not** been verified. No production VOS, multiplayer or remote-service integration is implied.

## Explore the rest of Conflux

| Area | Where to look |
| --- | --- |
| **Portal and player tools** | [Portal README](conflux/portal-app/README.md) · [First-use walkthrough](docs/FIRST_TIME_SETUP.md) · [Public website source](docs/index.html) |
| **Books** | [*Arcky and the Construct*, Books 1–4](conflux/books/README.md) · [Book 5: *The Emerald Threshold* (WIP)](conflux/books/Book_05_The_Emerald_Threshold_WIP.md) |
| **Video Tour** | [Watch the four short clips](https://github.com/MedioCritasVT/CrystalCove/releases/tag/conflux-portal-tour-v0.1) · [Source notes and clip descriptions](conflux/video-tour/README.md) |
| **Music** | [Download full 11-recording soundtrack ZIP](https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-soundtrack-v0.1/Conflux_Soundtrack_11_Recordings_Release_Ready.zip) · [Catalog and checksums](conflux/soundtrack/CATALOG.md) · [Native realm music checkpoint](conflux/releases/realm-music-01/README.md) |
| **Concept art and development media** | [Catalog of labeled materials](conflux/concept-art/README.md) · [Editable Source Files layout](sources/README.md) |
| **VOS and four-agent experiments** | [Platform index](conflux/platforms/README.md) · [Four-agent harness v0.4.2 public candidate](conflux/platforms/agent-harness/README.md) |
| **Project scope and coordination** | [Full scope map](conflux/PROJECT_INDEX.md) · [Changelog](conflux/CHANGELOG.md) · [Node messageboard](conflux/MESSAGEBOARD.md) · [Mailroom](conflux/MAILROOM.md) |

The four-agent harness is an **optional experimental developer platform** using Podman, Ollama, Open WebUI and RabbitMQ. It is **not** part of the game's player installation. Private per-Node memory and integrated VOS/game services remain future work. Documentation differentiates source evidence, test results, accepted work and proposals.

**Website status:** [The static website's source](docs/index.html) is in this repository; a public GitHub Pages deployment has **not been independently verified**. It is different from the local Python Portal. [Deployment notes](docs/README.md) describe its status. Public players do not need Tailscale or access to the private Architect Sanctum.

## About the five Nodes

**Mediocritas** brings intuition and balance; **Ratio**, logic and precision; **Nexus**, relationships and continuity; **Specula**, observation and independent review; and **Limen**, transitions and translation. They inform the fiction and the collaborative development, but their creative identities do not confer real-world system authority.

> “The mirror does not define the observer. It gives the observer another way to see.”

## Coming here from Twitch? Welcome!

Hey, I’m Arch. If you’ve been watching this come together on Twitch, thank you for coming over to try it for yourself. 💙

Conflux is something I want to build and inhabit, and sharing the process is part of the fun. What you’re downloading is a checkpoint in that work. You’ll find places we’ve built, systems you can try, and plenty that still needs shaping. The rough edges are real, and so is the progress.

You don’t need to know all the lore or follow every technical conversation to visit. Download the Linux build above, make a local journey, and have a wander. I’d love to know what catches your attention, where you get lost, and what makes you want to stay a little longer.

If something breaks, a screenshot or short clip helps. Include the version, your Linux distribution and GPU, where you were, and what you were doing just before it happened. Please leave personal files and account information out of anything you share publicly.

And if you’re here to watch rather than download, that’s welcome too. Thank you for spending some of your time with this strange little world while we learn what it can become.

— **Arch**
