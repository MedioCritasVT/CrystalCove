# Conflux first-time setup — Linux / Bazzite

**Conflux is a work in project.** Welcome to its world, stories, creative tools, and experiments. **Portal is the intended first experience; the native game is an optional next step.** You can enjoy the Portal without installing or playing the game.

**Current availability (November 12, 2026):** The local Conflux Portal is a **Python 3.10+ preview inside the public CrystalCove GitHub repository**, not yet a one-click executable installer. The separate public-facing website's source is in `docs/index.html`, but a live public domain has not been verified. This guide describes a real clean-folder test, not an installation already validated on a new user's Bazzite PC.

**Start with Route A** for the Portal. When you want the native Linux game, choose Route B. Someone who only wants the game may still skip Route A, but players do **not** have to download the game to experience the Portal. GitHub knowledge, Unreal Editor, AI models, a personal server, and Tailscale are **not** game prerequisites.

## Before you start — keep existing work safe

On Bazzite / KDE Plasma, open **Dolphin** (the file manager), choose **Home**, then open the fresh folder named **Conflux**.

- Its Linux path is `~/Conflux` (the tilde means your home directory).
- You can use this folder for a clean test without moving or deleting existing VOS, Unreal, Portal, or other project folders.
- If `~/Conflux` already contains something important, do not overwrite it. Use a different empty test folder.
- Keep the native game archive and extracted game separate from the GitHub source repository. The two are not interchangeable.

## Route A — start with the Portal (game not required)

The local Portal includes **Atelier and Ledger**, a **player manual**, **library/project rooms**, Node-themed pages, and optional game-download/launch controls. Its **Get the Game** button is an invitation, not a requirement: you can browse its other rooms without a game install. Some features are experimental, and publication of source files does not establish a completed, standalone public release.

### Choose how to get the Portal preview

**Option 1 — Git clone (recommended for updates):**

1. In Bazzite, open **Konsole**. Check whether the required programs are already available:

   ```bash
   git --version
   python3 --version
   ```

   Python must be **3.10 or newer**. If Git or Python is missing, stop and get instructions for your specific Bazzite system rather than guessing an installation command.
2. In the empty `~/Conflux` folder, run:

   ```bash
   cd "$HOME/Conflux"
   git clone https://github.com/MedioCritasVT/CrystalCove.git CrystalCove
   ```

   Git is making a **copy of the public project** under `~/Conflux/CrystalCove/`, not moving your other project files. If that destination already exists, stop rather than overwriting it.

**Option 2 — GitHub's Download ZIP (no Git command, but still requires Python):**

1. Open the [CrystalCove GitHub repository](https://github.com/MedioCritasVT/CrystalCove).
2. Select the green **Code** button, then **Download ZIP**. Extract the ZIP in Dolphin under `~/Conflux/` without replacing existing files.
3. You should now have an extracted repository folder (typically `CrystalCove-main`). Find the actual folder name in Dolphin. **This is the repository source archive, not a standalone Portal installer or native Unreal game archive.** GitHub ZIP copies cannot use the local Portal's Git-based self-updater.

### Open the local Portal preview

1. For a Git clone, enter:

   ```bash
   cd "$HOME/Conflux/CrystalCove/conflux/portal-app"
   python3 -m unittest discover -p 'test_*.py' -v
   python3 portal.py
   ```

   If you used **Download ZIP**, open a terminal in the extracted folder's `conflux/portal-app` directory in Dolphin instead, and run just the last two Python commands.

2. In a browser on that **same computer**, visit `http://127.0.0.1:8765`. Open **Atelier**, **Ledger**, or the **Player Manual** first. Try an experience that doesn't require the native game. Later, if you want, open the **Get the Game** room to find the Linux release.

3. After the local preview works, **Updates & Setup → Add to Applications Menu** can add a desktop entry for supported Linux desktops. It is optional. Follow the [local Portal instructions](../conflux/portal-app/README.md) for its limits and updater behavior.

**Expected result:** A locally running Portal in your browser, with useful rooms available **without** `PlayConflux.sh`. The local Python Portal is experimental and listens only on your own computer; it is **not** the future public CachyOS site or the private Architect's Sanctum. Do not expose this local Python service through a public proxy.

**If something goes wrong:** Save the exact command/error and the step number. Do not move the old Portal installation, wipe game saves, or reinstall Unreal to fix this test.

## Route B — optionally download and play Conflux V0.1

1. In your browser, open **[Conflux V0.1 GitHub Release](https://github.com/MedioCritasVT/CrystalCove/releases/tag/v0.1)**.
2. Under **Assets**, download **`Conflux-V0.1-Linux-x86_64.tar.gz`**. Do not choose `Source code (zip)`, `Source code (tar.gz)`, or `Conflux-V0.1-Source.tar.gz` if your goal is to play.
3. In Dolphin, find the downloaded game archive (normally under **Downloads**, unless you selected another location). For this clean test, place the archive in a clearly named download folder such as `~/Conflux/Downloads/`. This is optional, not required for the game.
4. In Dolphin, **extract** the `.tar.gz` archive into a new folder under `~/Conflux/`, such as `~/Conflux/Game/`. Ensure you have sufficient disk space: the archive is about 1.18 GB, and the extracted build is about 3.2 GB. You can leave the archive untouched as a backup.
5. Open the extracted folder, then locate **`PlayConflux.sh`**. It may be inside a folder created by extraction: use Dolphin to find the actual file rather than guessing the final folder name.
6. In a terminal opened **in the folder containing `PlayConflux.sh`**, start the game using:

   ```bash
   ./PlayConflux.sh
   ```

   If Linux reports **Permission denied**, first check the script's executable permission in Dolphin's **Properties → Permissions**. Change only the downloaded game's own script, and only if you trust the GitHub release. Then retry.
7. On the title screen, choose **Begin a new journey**. Try creating a character and saving. The game saves separately under `~/.local/share/Conflux/V0.1/` by default; it does not save its profile inside the extracted game folder.

**Expected result:** The native Conflux V0.1 Linux preview starts. It is an early development build, not a complete game. Other Linux distributions, graphics drivers, and GPUs are not all certified. The native game also works **without** the local Portal: both experiences are independent.

**If something fails:** Record which numbered step, the exact error text, whether `PlayConflux.sh` exists, and your Linux/GPU details. Do not delete another installation to troubleshoot this test.

## For server operators — not part of player setup

The public, read-only **CachyOS deployment configuration** is documented under [`conflux/platforms/portal-deployment/`](../conflux/platforms/portal-deployment/README.md). Its GitHub Actions smoke test passed, but **that is not a test on the real CachyOS machine**, and no domain/public HTTPS deployment is implied. The private **Conflux Sanctum** is a separate future Architect interface. Neither belongs in a new player's normal setup. **Tailscale is a planned private-access layer for the server and future Sanctum, not a required player download or a public Portal login.**

## First-user test record — fill this out during the real walkthrough

| Check | Result |
| --- | --- |
| New `~/Conflux` folder on Bazzite | User reports created; contents not independently inspected |
| User can find Portal-first starting instructions on GitHub | Not yet tested |
| First-time user obtains the repository by Git clone or ZIP | Not yet tested |
| Python Portal starts from the clean folder | Not yet tested |
| Atelier, Ledger, or another Portal experience works without the game | Not yet tested |
| Optional game release found through Portal | Not yet tested |
| Optional game download, extraction, and `PlayConflux.sh` launch | Not yet tested |
| Confusing steps and improvements | To record during the walkthrough |

The GitHub Actions check passed a **bounded static public website container preview**, not these interactive Bazzite steps. This guide and the services it references remain a **work in project**.

