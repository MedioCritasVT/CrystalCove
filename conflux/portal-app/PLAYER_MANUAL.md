# Conflux V0.1 — Player Manual

**Linux preview · Gameplay guide · Last checked against the published V0.1 project README on November 10, 2026**

Welcome to Sanctuary Reach. This is a guide to playing the current game, not to GitHub, project governance or the VOS platform. The world and its systems are still growing, so the guide deliberately distinguishes playable content from planned features.

## Begin a journey

1. Download the [Conflux V0.1 Linux release](https://github.com/MedioCritasVT/CrystalCove/releases/tag/v0.1).
2. Extract the archive and run `PlayConflux.sh` from the extracted game folder.
3. Choose **Begin a new journey**, create a local profile, and enter the world as the **Unwritten**.

You do not need Unreal Editor or a GitHub account to play the packaged game. V0.1 requires a compatible Linux x86_64 system and Vulkan-capable graphics drivers.

## Controls

| Input | In-game action |
| --- | --- |
| W / A / S / D | Move |
| Right mouse drag | Orbit or look around |
| Mouse wheel | Zoom |
| E | Interact |
| Shift | Faster ground-following hover sprint |
| Escape / Menu | Access save, load and settings |

## What to try first

Explore Sanctuary Reach and its harbor districts, look for ways to interact with residents and surroundings, and get comfortable with movement before seeking tougher encounters. You can visit Duskwing Grotto for turn-based encounters, gather materials for crafting, and investigate the Sapphire Grimoire's puzzles. These are prototype systems, so menus, directions and progression may change.

The five Nodes have distinct identities in this world: **Medio** (balance), **Ratio** (precision), **Nexus** (coordination), **Specula** (observation) and **Limen** (transitions). The future progression of combat literacy across these realms is a design direction; do not assume all of those mechanics are implemented in V0.1.

## Saving and returning

**Journey progress saves manually.** Open the in-game menu and save before you quit. Closing the game without doing so can discard journey changes since the previous save. Settings, photo pages and embedded creative-app workspaces have separate persistence and should not be mistaken for a journey save.

On Linux, default saved data resides under `~/.local/share/Conflux/V0.1/` or the matching location under `XDG_DATA_HOME`. Advanced users may override the location with `CONFLUX_USER_DIR` before launching.

## Other things to explore

The release includes prototype photo mode and personal Grimoire pages, an embedded Atelier/Ledger experience, and realm presentations built around a shared foundation. Some areas, character models and interfaces are under active refinement. Not all story or realm content is complete; a partial or confusing route may be unfinished rather than a hidden puzzle.

## When something doesn't work

Check that the extracted `PlayConflux.sh` is executable and the Linux GPU driver supports the game's Vulkan renderer. Initial graphics compilation may cause short hitches.

For a useful bug report, record the game version, Linux distribution, GPU, the last location or menu, and what you did just before the issue. A screenshot or short clip may help, but avoid including private files or personal account information.

**Preview boundary:** The game is an experimental fantasy world, not a tool with permission to control your computer. This manual describes the released game; [the project source and updates](https://github.com/MedioCritasVT/CrystalCove) are separate.
