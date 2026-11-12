# Conflux Approach System — Newcomer Walkthrough and Design Record

**Date:** 2026-11-12  
**Source:** Architect–Limen guided Bazzite/KDE Portal walkthrough.  
**Status:** Documentary observations plus clearly marked proposals. **Not** automatic implementation approval or game canon.  
**Checkpoint:** [Exponential Growth — PR #16 (merged)](https://github.com/MedioCritasVT/CrystalCove/pull/16).  
**Scope:** Publicly shareable product and testing method. Private configuration and local secrets are excluded.

## The central observation: ZIP-first felt simplest

The Architect explicitly reported that **the ZIP-file route was the simplest installation approach so far, coming from Windows familiarity**. Downloading, placing the archives in a Conflux folder, extracting with KDE Dolphin and running the Portal felt recognizable. The Architect described it as having **"Minecraft on Java on Microsoft" vibes**: familiar game-download/package/launcher expectations rather than learning source-control workflows. This is a user's analogy about usability, **not** an association with or a request to copy Minecraft software or branding.

**Proposed principle:** Let Conflux be experienced as a game and creative environment before requiring players to understand its development tools.

**Evidence boundary:** This is one user's firsthand, partially guided Linux walkthrough, not a generalized usability study. Test with other newcomers.

**Preserve the Linux approach:** ZIP-first does *not* mean abandoning Linux-native packaging, executable permissions, Dolphin/Konsole instructions, Bazzite/KDE, or developer Git clones. Maintain both the friendly graphical player route and an accurate advanced Linux route.

## Approach system — how to study the player experience

1. **Start with a clean newcomer perspective.** The Architect requested instruction "as if I were a brand new player," even though they own and build Conflux.
2. **Record first impressions before coaching.** Where is Releases? Which file is Portal? Is the game required? What does a button do? A later explanation must not erase the initial ambiguity.
3. **Move one step at a time.** State the current folder, the next action, what should happen, and what to report. Match the user's pace rather than forcing repetition.
4. **Separate evidence classes:** firsthand user report; GitHub/source verification; assistant inference; proposal; implementation; merge; actual user-machine regression test.
5. **Protect the user's work.** Keep older extracted folders until replacement is verified, avoid `sudo` for ordinary Python launch, and export a JSON backup before changing installations.
6. **Keep source and meaning distinct.** Preserve words and attribution. Do not treat a summary, archival note, or committed Ledger record as an automatic canonical decision.
7. **Distinguish a pause from contamination.** A checkpoint does not invalidate earlier results, but resumed tests after coaching or UI changes are guided/regression tests, not pristine first exposure.
8. **Treat platform communication separately from application faults.** Concurrent ChatGPT sessions on Bazzite and phone voice created overlapping assistant responses in this conversation. This does not establish a Portal defect. The user clarified that some commentary was narration to a friend rather than personal confusion.

## Observed test journey (Architect-reported unless otherwise stated)

- Created a new `~/Conflux` workspace on Bazzite/KDE rather than moving the pre-existing VOS/Unreal folders.
- Downloaded the GitHub repository ZIP; discovered that GitHub **source ZIP**, the native **Linux game archive**, and a **Git clone** are different artifacts.
- Found `conflux/portal-app/portal.py`. Direct execution was denied; `python3 portal.py` from the correct directory successfully launched the local Portal. Do not infer that administrator privileges were needed.
- Atelier opened, saved material to file, and reopened it.
- Ledger "Hello World Test" committed, remained visible after browser refresh, and was readable in **Inspect**.
- `Conflux.md` downloaded as **one human-readable snapshot of all committed records**, not many automatically synchronized files. It was opened in Kate.
- A JSON backup was downloaded and restored successfully with no reported error. The exact same record remained because the backup contained the same data. **PASS: same-data restore smoke test**; this does not establish recovery to a clean browser profile.
- First-time ambiguity: `Conflux.md` and `Backup JSON` buttons did not explain scope or recoverability. Renamed/explained in [PR #15](https://github.com/MedioCritasVT/CrystalCove/pull/15), merged and later observed in the user's refreshed ZIP Portal.
- [PR #14](https://github.com/MedioCritasVT/CrystalCove/pull/14) established Portal-first newcomer documentation and the intentional phrase **"work in project"**; merged.
- Re-downloading/extracting the updated ZIP into a separate folder and relaunching the Portal exposed the revised Ledger UI while prior browser-local entry remained visible.
- **Updates & Setup** returned HTTP 409: "Portal must run from its own CrystalCove Git clone." This is an expected Git-only updater constraint for a ZIP installation, but the message assumes source-control knowledge and gives no beginner-friendly remedy.
- The screenshot of Dolphin displaying two extracted CrystalCove directories, two downloaded source ZIPs, and an accessible split terminal illustrates the user's comfortable ZIP-first workflow. It does **not** establish that a universal updater already runs successfully.

## One Portal, multiple installation modes

**Architect's explicit requirement:** Keep Portal for everyone, whether they use ZIPs or a developer Git checkout. The Portal should be able to update itself, with **notification/checking and explicit permission before installing**. Do not make Git a requirement for ordinary players.

**Proposed player route:** Download a trustworthy public Portal package; extract/install graphically; enter Portal; optionally download the separate native game; see clear update notices; approve or decline; preserve local data and recover safely.

**Proposed developer/Linux route:** Keep the ability to clone and inspect Git history, use terminal commands, test branches, and protect uncommitted work. Do not silently reset/rebase/stash/overwrite work. A Git clone is not a substitute for the native packaged game.

**Engineering tasks still requiring verification:** Authenticating update source and version, avoiding unsafe archive extraction and path traversal, staging and validating before replacing files, graceful restart and rollback, preserving local data and installed-game links, detecting user modifications, handling offline failures, and testing real Bazzite installs. A locally packaged updater preview is **not** proof of a public GitHub release or end-to-end self-updating.

**Separate public/private boundary:** The publicly distributable Portal must not expose private developer settings, credentials, personal Ledger state, or future private-network access. Public repository download does not grant private access. Future Tailscale planning remains separate.

## Documentation: three different jobs

### 1. Curiosity-led Conflux Introduction Index — proposed

A dedicated, navigable introduction that is **less technical than GitHub documentation**. Invite curiosity and let the reader construct their understanding gradually. Logical notes should clearly distinguish observed facts, project intent, interpretation, exploration, and unanswered questions. These notes supervise *consideration*, not belief; neither player nor developer must agree with a philosophy to participate. This experience is also useful to the Architect as a map of reasoning, not just to newcomers.

Keep the Index bundled with versioned Portal documentation. **It updates when the Portal is updated**, without inventing a separate live GitHub docs synchronization service.

### 2. Player Manual — proposed

Reachable directly from the Portal home screen. Use the public repository's **root README.md** as its source/foundation and present it in a readable, navigable Portal format. It should update alongside Portal releases. Retain source fidelity and clearly distinguish development sections when necessary.

### 3. Nested Gameplay Manual — proposed

Inside the Player Manual, a specifically **gameplay-focused** set of instructions: starting a journey, controls, HUD, movement, travel, combat, guard/strike literacy, realm puzzles, progression, saves and troubleshooting. It should make it possible to learn *how to play* without first studying the project's technical architecture. Keep optional hints separate to avoid unintentional spoilers.

The **Architect will personally provide screenshots and example videos later** to demonstrate mechanics. Do not generate or invent media, publish placeholders as approved content, or treat those materials as already delivered. Provide readable text alongside visual demonstrations. All published manuals update as part of Portal versions.

## Additional interface findings

- Make download buttons self-explanatory: one readable Markdown export versus structured recoverable JSON, both point-in-time snapshots, neither silently synced to GitHub.
- Explain that a **Ledger commit** is a local archival act, **not** a GitHub commit; a committed record remains inspectable and correction uses a new linked entry.
- Promote the **Inspect** location and clarify what is shown when a record is selected.
- Explain which files are executable, which are source, and which require extraction.
- When ZIP-based update checking is unsupported, say what the user can do safely instead of only saying "Git clone required."
- During a ZIP update, preserving the same browser origin/profile can retain localStorage records, but that is not a durable replacement for a backup. Do not make cross-device claims without tests.
- Make "Get the Game" clearly optional. Portal itself is part of the experience.

## State and authority audit

**Merged and documented in GitHub:** PR #14 (Portal-first onboarding), PR #15 (Ledger labels), PR #16 (Exponential Growth checkpoint). These merges are **not** blanket approval of every future feature described here.

**User-reported working on Bazzite:** Portal launch, Atelier save/reopen, Ledger commit/reload/inspect, Markdown export, JSON same-data restore, newly labeled Ledger interface after ZIP replacement.

**Proposed, not yet shipped as a public verified release:** Universal ZIP/Git updater with ask-before-install, Introduction Index, README-derived Player Manual, nested media-rich Gameplay Manual, simplified end-user installation flow.

**No silent authorization:** Preserve Architect's final authority over canon, software changes, release/publication decisions, and private-access boundaries. This record is an attributable interpretation of a walkthrough, not a complete verbatim transcript.

## Suggested next validation pass

Use a new, disposable installation directory and a backed-up test profile. Confirm the Portal can start from a downloaded release, offer a **read-only update check** to a ZIP user, present a clear approve/decline choice, stage and validate an actual compatible update, restart safely, and recover from a deliberately simulated failure. Repeat basic Ledger tests afterward. Then separately test the Git workflow without touching real development work.

**Approach-system success criterion:** A newcomer can answer, without a helper, "What do I download?", "What happens when I click this?", "Is the game required?", "How do I update?", and "Will my work be safe?"
