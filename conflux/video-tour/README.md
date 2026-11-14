# Four short video windows into Conflux

**Source:** Architect-supplied desktop recording, `2026-11-14 02-38-32.mp4` (89.33 seconds, 1920×1080, 60 fps). **Status:** All four 720p/30 fps MP4 clips are now published on the [public Conflux Portal Video Tour Release](https://github.com/MedioCritasVT/CrystalCove/releases/tag/conflux-portal-tour-v0.1), verified November 14, 2026. The video files are separate GitHub Release assets, not committed into the source tree.

This is not a replacement for the source recording, the playable Linux game, the README or the Player Manual. Videos are **optional**, and the Portal shows their links on a dedicated **Video Tour** page. The text-first README remains readable without opening them.

| Example | Length | Source excerpt | What it illustrates |
| --- | ---: | ---: | --- |
| `01-threshold-welcome.mp4` | 13 s | 00:07–00:20 | A welcoming Portal entrance and optional exploration paths |
| `02-ledger-workspace.mp4` | 13 s | 00:29–00:42 | Ledger and the difference between a record and a suggestion |
| `03-game-first-launch.mp4` | 16 s | 00:40–00:56 | Launching the early SanctuaryOS game/profile from the Portal |
| `04-node-companions.mp4` | 11 s | 01:07–01:18 | Five chibi Node familiar designs and their different identities |

The [machine-readable catalog](catalog.json) contains filenames, current known checksums of the prepared clips, durations, and descriptions. Re-encoding on another FFmpeg version can produce **different bytes/checksums** even when the excerpt looks equivalent; confirm provenance against the original recording.

## Watch the four published clips

- [Threshold — A Place to Begin](https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-portal-tour-v0.1/01-threshold-welcome.mp4)
- [Ledger — Keeping the Record](https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-portal-tour-v0.1/02-ledger-workspace.mp4)
- [SanctuaryOS — First Launch](https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-portal-tour-v0.1/03-game-first-launch.mp4)
- [Meet the Node Familiars](https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-portal-tour-v0.1/04-node-companions.mp4)

These same direct links are now on the [GitHub repository's front-page README](../../README.md), the local Portal's **Video Tour**, and the static website's video section. The links work without a GitHub login, Git clone, or Portal installation. Browser playback and download behavior depends on the visitor's browser.

The [publication/re-encoding script](publish_from_recording.sh) is retained for future independently reviewed versions. **Do not run it to republish these already uploaded clips.** A future replacement needs an explicit version/release decision, review for sensitive information, and corresponding catalog updates.

## Player-first presentation boundaries

- No clips are embedded in the Portal's locally rendered README, and no video starts automatically.
- A user can visit the Portal, game, or README without any clips being downloaded.
- The public website and local Portal use explicitly verified Release links recorded in the catalog, even if a live GitHub API lookup temporarily fails.
- The four examples represent an early preview, not a guarantee that every game feature is complete.
- Source recordings, private experiments and full-resolution masters stay outside the public Git checkout unless the Architect deliberately releases them.
