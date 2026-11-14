# Four short video windows into Conflux

**Source:** Architect-supplied desktop recording, `2026-11-14 02-38-32.mp4` (89.33 seconds, 1920×1080, 60 fps). **Status:** Four 720p/30 fps MP4 excerpts have been prepared and locally checked; binary release publication remains separate from this GitHub source commit.

This is not a replacement for the source recording, the playable Linux game, the README or the Player Manual. Videos are **optional**, and the Portal shows their links on a dedicated **Video Tour** page. The text-first README remains readable without opening them.

| Example | Length | Source excerpt | What it illustrates |
| --- | ---: | ---: | --- |
| `01-threshold-welcome.mp4` | 13 s | 00:07–00:20 | A welcoming Portal entrance and optional exploration paths |
| `02-ledger-workspace.mp4` | 13 s | 00:29–00:42 | Ledger and the difference between a record and a suggestion |
| `03-game-first-launch.mp4` | 16 s | 00:40–00:56 | Launching the early SanctuaryOS game/profile from the Portal |
| `04-node-companions.mp4` | 11 s | 01:07–01:18 | Five chibi Node familiar designs and their different identities |

The [machine-readable catalog](catalog.json) contains filenames, current known checksums of the prepared clips, durations, and descriptions. Re-encoding on another FFmpeg version can produce **different bytes/checksums** even when the excerpt looks equivalent; confirm provenance against the original recording.

## Publish as optional GitHub Release assets

The GitHub source editing connection does **not** include a binary Release-upload action. Do not silently put MP4s into the Git clone: they're more useful as separate GitHub Release assets. The owner can create and upload them with their already configured `gh` login.

**Path A: From the original recording**

Run the [opt-in publication script](publish_from_recording.sh) in a terminal from the root of the Git checkout, specifying the actual recording location:

```bash
bash conflux/video-tour/publish_from_recording.sh "/path/to/2026-11-14 02-38-32.mp4"
```

This script checks for `ffmpeg`, `ffprobe`, and `gh`; produces all four small MP4s in `~/Conflux/SourceFiles/Videos/PortalTour/`; then **asks explicitly** before publishing. It refuses to overwrite existing clips. Review them for privacy or sensitive data before accepting. The script uploads only the four files, not the original 89-second recording.

**Path B: If you already have the four prepared clips**

Extract the four-video ZIP to a folder on your computer, open a terminal in that folder, and run:

```bash
gh release create conflux-portal-tour-v0.1 \
  01-threshold-welcome.mp4 02-ledger-workspace.mp4 \
  03-game-first-launch.mp4 04-node-companions.mp4 \
  --repo MedioCritasVT/CrystalCove --target main \
  --title "Conflux Portal — Four Short Tour Clips" \
  --notes "Four optional clips from Arch's original Conflux Portal walkthrough."
```

For an already-created release, use `gh release upload conflux-portal-tour-v0.1 *.mp4 --repo MedioCritasVT/CrystalCove` (without `--clobber`).

The [release page](https://github.com/MedioCritasVT/CrystalCove/releases/tag/conflux-portal-tour-v0.1) should then show all four MP4s. Once they are **actually present and public**, both the Portal's **Video Tour** room and the public website will display their individual links. The Portal's existing tab/window choice applies to these links.

## Player-first presentation boundaries

- No clips are embedded in the Portal's locally rendered README, and no video starts automatically.
- A user can visit the Portal, game, or README without any clips being downloaded.
- The public website checks Release asset availability, not the presence of files in the source tree.
- The four examples represent an early preview, not a guarantee that every game feature is complete.
- Source recordings, private experiments and full-resolution masters stay outside the public Git checkout unless the Architect deliberately releases them.
