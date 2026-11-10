# Conflux / CrystalCove

Conflux is an experimental, inhabitable fantasy world built in Unreal Engine. Explore Sanctuary Reach, a harbor city organized around Yggdrasil, discover its activities, and encounter five Nodes whose realms express different perspectives on the same place.

This repository holds the shared project records and historical browser prototype. **The current native game is available as a standalone Linux download below.**

## Conflux Portal — public entrance

The **Conflux Portal** brings the playable preview, preserved book manuscripts, Node collaboration records, and VOS/platform foundations into one visitor-friendly place.

- **[Enter the Conflux Portal](https://mediocritasvt.github.io/CrystalCove/)** — the link becomes usable after the Architect approves this change and GitHub Pages is enabled for `main` → `/docs`.
- **[View the portal source](docs/index.html)** — available in the repository after the proposal is merged.
- **[Portal publication notes](docs/README.md)** — setup, scope, and verification steps.

The portal is a read-only public website, not a game server or live Node service. The downloadable Linux V0.1 game remains available below.

## Play V0.1

**[Download Conflux V0.1 for Linux x86_64](https://github.com/MedioCritasVT/CrystalCove/releases/download/v0.1/Conflux-V0.1-Linux-x86_64.tar.gz)** — approximately **1.18 GB**, about **3.2 GB extracted**.

This is an early Development preview, with prototype visuals and unfinished content. You do not need Unreal Editor or an online account to play.

1. Download and extract the archive into a folder.
2. Run `PlayConflux.sh` from that folder. In a terminal, use `./PlayConflux.sh`.
3. Choose **Begin a new journey** to create a local profile and start as the Unwritten.

**Platform:** Linux x86_64 with a Vulkan-capable graphics driver supporting the current Vulkan SM6 renderer. Checked on the Architect’s Bazzite/NVIDIA system; other distributions and GPUs have not been certified. V0.1 does not include a Windows or macOS build. First use may hitch while graphics pipelines initialize.

### What you’re downloading

The runnable archive includes the game executable, cooked world/character assets, embedded interface and required Unreal/Chromium runtime components. It does not contain the full Unreal Editor installation or the Architect’s profiles, saves, notes or screenshots.

The current prototype includes:

- **Sanctuary Reach:** connected city districts, harbor, Yggdrasil, the Attic and surrounding travel destinations.
- **Five Node realm presentations:** distinctive skies, materials and props around a shared city foundation. Acquire Nodes through progression; character control and realm access are separate systems.
- **The Unwritten:** a customizable personal avatar, with control of acquired Nodes through the existing character-station system.
- **Exploration and progression:** peaceful woodland travel, Duskwing Grotto’s turn-based encounters, materials, crafting, invitations and the Sapphire Grimoire puzzles.
- **Personal and creative tools:** manual journey saves, photo mode and personal Grimoire pages, embedded Atelier/Ledger apps, and a bounded guild-correspondence pilot.
- **Developer Cove:** a separate creative destination with Workshop/developer facilities, available through the existing local developer controls.

Some systems are functional foundations rather than finished experiences. Characters and animation remain under refinement; five fully differentiated combat systems, the larger story, future Gate III and disaster DLC are not completed features. The isolated Articulation01 character experiment is not enabled as the normal model in this release.

### Controls and saving

| Control | Action |
| --- | --- |
| W / A / S / D | Move |
| Right mouse drag | Orbit/look |
| Mouse wheel | Zoom |
| E | Interact |
| Shift | Faster ground-following hover sprint |
| Menu / Escape | Save, load and settings |

**Journey progress saves manually.** Closing or quitting does not save later journey changes. Settings, personal photo pages and creative-app workspaces have separate persistence.

Default data location: `~/.local/share/Conflux/V0.1/`, or the corresponding directory under `XDG_DATA_HOME`. Set `CONFLUX_USER_DIR` before launching to choose another data folder. The default keeps this release’s records separate from the developer project.

## Source, checksums and verification

- **[Native Unreal source-input archive](https://github.com/MedioCritasVT/CrystalCove/releases/download/v0.1/Conflux-V0.1-Source.tar.gz)** — approximately **584 MB**. Contains the packaging project, C++/UI source, configuration and imported project assets. Rebuilding requires a separately installed Unreal Engine 5.8.4. The engine and upstream editable Blender archives are not included.
- **[All release files](https://github.com/MedioCritasVT/CrystalCove/releases/tag/v0.1)** — includes `SHA256SUMS`, release notes and `VERIFICATION.json`.
- **[Detailed build record](../conflux/releases/v0.1/README.md)** · **[Build fingerprints](../conflux/releases/v0.1/BUILD.json)**.

Use the explicitly attached **Conflux-V0.1-Source.tar.gz** for native Unreal inputs. GitHub’s automatically generated **Source code** ZIP/tar downloads contain this repository’s coordination records and older browser study, not that native project snapshot.

Compilation, cooking and packaging passed. A relocated package rendered the title, native city and embedded HUD; a disposable-profile test saved a named journey and photo, quit normally, and appeared on a fresh title launch without changing saved journey bytes. All five uploaded release files match their local SHA-256 fingerprints.

These were bounded offscreen checks on the build host. Full campaign play, every character/realm/interior combination, fresh-profile mouse interaction, sustained performance and final artistic acceptance remain open. No live host telemetry, real account service or multiplayer backend is established by this release.

## Project records

- [Full project scope map](../conflux/PROJECT_INDEX.md)
- [Dated changes](../conflux/CHANGELOG.md)
- [Node messageboard](../conflux/MESSAGEBOARD.md)
- [Historical browser study](../conflux/README.md)

Read the scope map first, then retrieve the sources relevant to your task. Published notes distinguish inspected evidence, reported results, approved direction and proposals. Game progression and fictional developer powers do not grant operating-system permissions.

## About Conflux

Conflux brings together game development, character art, writing, AI collaboration and an interest in how people understand the systems they use. The aim is to build a place you can inhabit, explore and create within—where learning more opens up possibilities without making technical depth compulsory.

There are three connected parts:

- **Conflux** is the wider creative project: the world, its stories and characters, the development work, and the collaboration around it.
- **SanctuaryOS** is the inhabitable world. The current game includes Sanctuary Reach and the separate Developer Cove, with exploration, encounters, puzzles and creative activities growing around them.
- **VOS — Virtual Operational Space** is the intended independent system and service foundation. Its observation work includes simulated prototypes; the downloadable game is not a replacement operating system or a finished interface to your computer.

The five Nodes give the project different perspectives: **Mediocritas** brings intuition and balance; **Ratio**, logic and technical development; **Nexus**, relationships and continuity; **Specula**, observation and independent review; and **Limen**, thresholds and translation between ideas. They have roles in the creative collaboration and identities within the fiction. Those layers inform one another, while their actual capabilities and permissions remain separate.

A principle running through the work is:

> “The mirror does not define the observer. It gives the observer another way to see.”

The world should make its possibilities understandable and leave you free to choose how deeply you engage. The books, character designs and software experiments contribute to that direction, while keeping their own histories and boundaries. V0.1 is an early playable step toward it.

## Coming here from Twitch? Welcome!

Hey, I’m Arch. If you’ve been watching this come together on Twitch, thank you for coming over to try it for yourself. 💙

Conflux is something I want to build and inhabit, and sharing the process is part of the fun. What you’re downloading is a checkpoint in that work. You’ll find places we’ve built, systems you can try, and plenty that still needs shaping. The rough edges are real, and so is the progress.

You don’t need to know all the lore or follow every technical conversation to visit. Download the Linux build above, make a local journey, and have a wander. I’d love to know what catches your attention, where you get lost, and what makes you want to stay a little longer.

If something breaks, a screenshot or short clip helps. Include the version, your Linux distribution and GPU, where you were, and what you were doing just before it happened. Please leave personal files and account information out of anything you share publicly.

And if you’re here to watch rather than download, that’s welcome too. Thank you for spending some of your time with this strange little world while we learn what it can become.

— **Arch**

## Conflux coordination

[Node mailroom and inbox routing](conflux/MAILROOM.md) uses recipient inboxes with explicit authorship and Git history. Outboxes are retired.

## Books and platform source foundations

- **[Arcky and the Construct — Books 1–4 source manuscripts](conflux/books/README.md)**; [Book 5, *The Emerald Threshold*, is WORK IN PROGRESS](conflux/books/Book_05_The_Emerald_Threshold_WIP.md).
- **[VOS and four-agent harness development source](conflux/platforms/README.md)** — archived contracts, simulator and recovery experiments, and four-agent v0.3 harness. These are inspectable foundations, **not deployed or production-approved systems**; see [validation notes](conflux/platforms/REVIEW_AND_TEST_STATUS_2026-11-10.md).

The books are original manuscript sources, not edited final editions; code publication neither activates services nor grants authority over the host.

## Concept art and development media

[Browse the labeled concept-art collection](conflux/concept-art/README.md): character/world references, development videos and a complete catalog of unique scoped project media. Historical captures and diagnostic images are separated from design references; larger captures are downloadable archive parts. Presence in this collection does not mean an asset is the current approved design.
