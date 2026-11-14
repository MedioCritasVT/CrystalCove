# README previews — short motion examples and Node Companions

These are public-facing **examples of what the Portal looks and feels like**, not a replacement for the game, manual, or released video files. They are deliberately small so that visitors can explore the repository without downloading a full game or videos.

The four animated GIFs use the [already-public Portal tour MP4s](../../conflux/video-tour/README.md) as their sources. They are reduced to 560-pixel-wide, 7 FPS, four-second loops with a restricted palette and no audio. The fifth image is a screenshot captured from the actual local Portal's **Node Companions** page; the music dock is hidden for clarity in the screenshot only.

| Filename | Purpose |
| --- | --- |
| `01-threshold-preview.gif` | The welcoming Threshold and independently optional rooms |
| `02-creative-workspace-preview.gif` | The creative workspace (Atelier/Ledger) |
| `03-gameplay-preview.gif` | Transition from Portal to the early SanctuaryOS game |
| `04-library-music-preview.gif` | Library & Art room; soundtrack is available separately |
| `05-node-companions.png` | All five distinct Portal chibi designs and their links to source panels |

**Precision note:** the fourth public MP4 was initially distributed as `04-node-companions.mp4`, but its visible excerpt primarily demonstrates the **Library & Art** room. The screenshot supplies the requested separate, more accurate Node Companions example. The clip filename is kept stable rather than renaming an already published Release asset.

## Reproduce

From the repository root, with `curl`, `ffmpeg`, a locally available Chrome browser, and Python packages `playwright` and `Pillow`, run:

```bash
bash docs/previews/render_previews.sh
```

The script verifies the original four Release MP4 SHA-256 values before rendering. It does not use files from a private home directory, launch the native game, connect to VOS, start music, or modify a user's installation. The Node screenshot script starts a temporary loopback Portal and renders its actual HTML/CSS, then closes the server.

GIFs are short and loop automatically on GitHub. People who prefer still images can view the Node PNG or open the optional individual MP4 links instead. A Git clone includes these small documented previews but **not the larger source videos**.
