# Conflux Portal — Linux local preview

**Status:** Source-code preview, not a signed installer or security-reviewed release. This iteration proposes a per-menu Atelier/Ledger identity and an explicit, beginner-friendly game download and installation discovery workflow. No VOS host control is enabled.

## Run locally

Python 3.10 or later is required. From the cloned **CrystalCove repository root**:

```bash
cd conflux/portal-app
python3 -m unittest test_portal.py -v
python3 portal.py
```

If you are already in `conflux/portal-app`, skip the `cd` command. Open `http://127.0.0.1:8765`. Keep the port stable: the bundled Atelier and Ledger each use browser-local storage, which is specific to your browser profile and the exact origin (including port).

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

## Other ready applications

**Conflux Atelier (Medio/Nexus)** and **Conflux Ledger (Ratio/Limen)** are bundled original HTML apps. Their **Open** buttons work with no installation or executable registration. Export backups regularly, especially before clearing browser data or switching browsers.

The **Player Manual** contains actual gameplay guidance. **Book 5** remains a labeled literary WIP with Chapters 3–10 currently in GitHub. **Concept Art** links to Ratio's labeled archive, not yet an approved final-asset gallery. Node character/pet illustrations remain pending. **VOS** remains disconnected and does not collect machine telemetry.

## Color and section map

The colors are derived from the original standalone applications rather than inventing a third unrelated scheme:

| Portal section | Identity |
| --- | --- |
| Threshold | Medio amber `#e9bf84` × Nexus violet `#c2a4f3` |
| Applications | Both pairs together: Atelier amber/violet, Ledger Ratio blue/Limen green |
| Get the Game | Medio amber × Ratio blue (invitation meets precision) |
| Game folder finder | Ratio blue `#84bff3` × Limen green `#9cdec0` (evidence and transition) |
| VOS Instruments | Ratio blue × Limen green |
| Library & Art | Nexus violet × Medio amber |
| Node Companions | Each Node's own accent; artwork placeholders are explicitly labeled |
| Player Manual | Medio amber × Limen green (guidance at a threshold) |

Text contrast, keyboard focus and mobile layout retain priority over ornamental treatment.

## Safety and known limitations

The Portal listens on **127.0.0.1** only; **do not expose it through a proxy or public network**. POST actions require same-origin authorization and the server's per-session token. The native folder chooser is invoked only by clicking the button; there is no automatic home-directory scan, shell-command interpolation, or automatic execution of discovered applications. Even so, this is an **experimental local launcher, not a security-audited service**.

Local folder selection is supported only when `kdialog` or `zenity` is installed and accessible to the Python process; manual absolute-path search is the fallback. The finder does not automatically discover apps outside the chosen folder or inspect packed `.tar.gz` contents. There is no auto-installer, auto-updater, background agent or automatic synchronization with GitHub yet.

Test locally using `python3 -m unittest test_portal.py -v`. The repository also has `.github/workflows/portal-smoke.yml` for non-destructive GitHub Actions validation; tests must pass before public release. These tests cover routes, app status, bounded scanning, symlink rejection, permission checks, explicit registration and JavaScript syntax. They do not substitute for a hands-on Linux desktop picker or full game-launch test.

**Governance:** proposal, test result, merge and deployment are distinct. The Architect retains review and approval authority.
