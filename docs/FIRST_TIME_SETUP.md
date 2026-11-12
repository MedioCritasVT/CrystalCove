# Conflux first-time setup — Linux / Bazzite

**Status (November 12, 2026): beginner instructions proposed for review and a real clean-folder test.** This guide is not evidence that a fresh installation has been completed on a player's machine.

**Start here:** You do **not** need Git, the Unreal Editor, an AI model, a server, or the local Portal app just to play Conflux V0.1. Do not download GitHub's green **Code → Download ZIP** expecting a playable game. The game is a separate **Release** download.

This guide describes two routes. Try **Route A** as a new player first. Use **Route B** only if you also want to inspect the GitHub project and try the optional local Portal application.

## Before you start — keep existing work safe

On Bazzite / KDE Plasma, open **Dolphin** (the file manager), choose **Home**, then open the fresh folder named **Conflux**.

- Its Linux path is `~/Conflux` (the tilde means your home directory).
- You can use this folder for a clean test without moving or deleting existing VOS, Unreal, Portal, or other project folders.
- If `~/Conflux` already contains something important, do not overwrite it. Use a different empty test folder.
- Keep the native game archive and extracted game separate from the GitHub source repository. The two are not interchangeable.

## Route A — play the game, no Git commands required

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

**Expected result:** The native Conflux V0.1 Linux preview starts. It is an early development build, not a complete game. Other Linux distributions, graphics drivers, and GPUs are not all certified. The browser Portal is **not** required for this route.

**If something fails:** Record which numbered step, the exact error text, whether `PlayConflux.sh` exists, and your Linux/GPU details. Do not delete another installation to troubleshoot this test.

## Route B — explore GitHub and try the optional local Portal

This route is for someone who wants the project files and developer/local Portal preview. **Cloning the repository does not download or install the native Unreal game.** It also does not grant access to private Sanctum or server administration.

### What the GitHub buttons mean

- **Releases** — packaged downloads intended for players (Route A).
- **Code** — the repository's source and project records; not the native game installer.
- **Pull requests** — proposed changes. Merged changes land on the repository's main branch.
- **README** — the repository's front-page instructions.
- **Clone** — make a local working copy of the repository, which can fetch later updates.

### Set up a clean Git clone

1. In a terminal, check that Git and Python are available:

   ```bash
   git --version
   python3 --version
   ```

   The local Portal needs Python 3.10 or newer. If either command is not found, **stop and ask for installation guidance for your actual Bazzite setup** rather than guessing a package command.
2. From your new project folder, create a separate repository copy:

   ```bash
   cd "$HOME/Conflux"
   git clone https://github.com/MedioCritasVT/CrystalCove.git CrystalCove
   ```

   This creates `~/Conflux/CrystalCove/`. It does not move, replace, or modify your older project directories.
3. To see the public website's source in Dolphin, open `~/Conflux/CrystalCove/docs/index.html`. It is a **static public preview**, not the locally installed Python Portal, not a deployed public domain, and not the game.
4. To try the **separate, experimental local Portal**, run:

   ```bash
   cd "$HOME/Conflux/CrystalCove/conflux/portal-app"
   python3 -m unittest discover -p 'test_*.py' -v
   python3 portal.py
   ```

   In a browser on **that same computer**, open `http://127.0.0.1:8765`. This local application includes Atelier, Ledger, and game-launcher features. It is not a production public website and must not be exposed through a public proxy.
5. The local Portal has an optional **Updates & Setup → Add to Applications Menu** step. Its built-in updater works with a valid Git checkout; the repository **ZIP** does not provide the same updater functionality. Do not run the updater on a working branch with edits you want to preserve without checking its instructions.

**Expected result:** You have a separate `CrystalCove` source directory inside `~/Conflux`, and the optional local Portal can be tested independently of the native game.

**If `~/Conflux/CrystalCove` already exists:** Do not run `git clone` into it again or overwrite anything. Inspect the existing folder before deciding how to update it.

## For server operators — not part of player setup

The public, read-only **CachyOS deployment configuration** is documented under [`conflux/platforms/portal-deployment/`](../conflux/platforms/portal-deployment/README.md). Its GitHub Actions smoke test passed, but **that is not a test on the real CachyOS machine**, and no domain/public HTTPS deployment is implied. The private **Conflux Sanctum** is a separate future Architect interface. Neither belongs in a new player's normal setup.

## First-user test record — fill this out during the real walkthrough

| Check | Result |
| --- | --- |
| Clean `~/Conflux` test folder | Not independently verified |
| Player can find the correct GitHub Release asset | Not yet tested with the Architect |
| Download and extraction understood | Not yet tested |
| `PlayConflux.sh` launched on fresh setup | Not yet tested |
| Optional clone created without disturbing old files | Not yet tested |
| Optional `portal.py` works from the fresh clone | Not yet tested |
| Confusing steps and proposed documentation fixes | To record during the walkthrough |

Keep the distinction clear: **GitHub CI passed a bounded static-website container test; it did not prove any of the steps above on Bazzite.**
