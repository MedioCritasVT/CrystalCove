# Exponential Growth — Conflux first-time Portal checkpoint

**Date:** 2026-11-12  
**Source:** Architect–Limen guided first-time Bazzite/KDE player walkthrough; Architect reports for local UI observations.  
**Status:** Documentary checkpoint proposed for review; not a game-canon decision and not proof of tests beyond those listed here.  
**Authority:** Architect retains decisions on project changes, interpretation, and canon.

## Why checkpoint now?

The Architect chose the name **Exponential Growth**, requested that the present results and rationale be preserved, and asked whether **pausing to create a checkpoint contaminates the testing process**.

**Answer:** A pause does not invalidate observations made before the pause. However, discussion, coaching, code changes, and repeated use can make subsequent actions *no longer a pristine first-time encounter*. Therefore distinguish:
- **Before explanation/change:** user's actual confusion, first discovery, or original behavior.
- **After explanation/change:** guided operation, regression verification, or a newly updated interface.
- **Independent verification:** GitHub state and file/source inspection, not proof of behavior on the user's computer.
Do not backfill later understanding into what the user initially knew.

## User-reported hands-on results

1. **Clean ZIP extraction / local run on Bazzite KDE:** Downloaded GitHub repository ZIP into a new `~/Conflux` workspace. Found `conflux/portal-app/portal.py`. Direct execution produced a *permission denied* error; starting with `python3 portal.py` worked without `sudo`. Portal was accessed at `http://127.0.0.1:8765`.
2. **Atelier save/reopen:** A note was saved to a local file and reopened; matching text was observed.
3. **Ledger commit/persistence:** Test record `Hello World Test` was committed. It remained in **Committed Entries** after a browser refresh; **Inspect** showed the original details.
4. **Markdown export:** The **Conflux.md** button downloaded a readable Markdown snapshot. The user opened it in Kate and found the test record. Source inspection confirmed that the export groups approved records separately from other committed records. This is one snapshot of all committed entries, **not a live synchronized file** and not a bundle of unrelated files from disk.
5. **Usability finding:** The original labels `Conflux.md` and `Backup JSON` did not explain whether downloads covered one or all entries, whether they were for reading or recovery, or whether they updated automatically. The route from selecting a record to reading its details in **Inspect** was also initially unclear.
6. **Interface improvement:** GitHub PR #15 added descriptive labels **Download readable Ledger (.md)**, **Download restorable backup (.json)**, and **Restore from backup**, with upfront explanations. PR #15 was merged to `main`. User downloaded an updated repository ZIP, extracted it separately, ran the updated Portal, saw the new label, and reported the pre-existing test entry was still present.
7. **JSON backup and restore:** The user downloaded a JSON backup and **successfully restored that backup** in Ledger. The process completed **without errors**. Inspect displayed the same record afterward because the backup contained the **identical record/data** already stored. **Result: PASS — same-data JSON restore smoke test.** This verifies that the restore flow accepted that backup and preserved its content without reported error. It does **not** independently test restoring to a clean/empty browser profile, recovering deleted entries, changing records, or cross-device portability.
8. **No unwanted deletion/privilege escalation:** The walkthrough explicitly avoided `sudo`, preserved prior extracted Portal files during update, and treated the downloaded JSON as a recovery artifact. No user-side file deletion was required for the test.

## GitHub changes and boundaries

- **PR #14:** Portal-first onboarding documentation — merged to `main`. Portal rooms can be explored without downloading the game.
- **PR #15:** Ledger export/backup wording improvements — merged to `main` and newly displayed in the user's refreshed ZIP-based Portal.
- The separate **Conflux game** release is optional and distinct from updating Portal source. A roughly 1.1 GB archive is likely the game release, not the repository ZIP.
- The user's **browser-local Ledger** is not a GitHub commit or shared SQLite/agent memory store. The ZIP reinstall/relaunch test preserved access in the same browser origin. Do not claim durable cross-browser/cross-machine persistence.
- No CachyOS host deployment, public launch, game playthrough, or security audit was tested by these observations.

## Reproducible UX improvements to consider

- Beginner guide should give an explicit **ZIP update path**: back up JSON first; download fresh ZIP; extract without overwriting old folder; run `python3 portal.py` from `conflux/portal-app`; check same address and browser; verify records.
- Explain why direct file execution can fail with `permission denied`, and that `sudo` is **not** appropriate for launching Portal.
- Explain browser-local persistence, read-only Markdown snapshot versus restorable JSON, and that same-data restoration looks unchanged *by design*.
- Keep new-player discovery logs distinct from after-the-fact coaching and post-merge regression results.

## Next steps / open questions

- Resume the **player-first Portal walkthrough** from the updated running version; avoid restarting the entire onboarding sequence.
- Continue other Portal rooms/manual, then optional game journey when the Architect chooses.
- Optional stronger restore test in a **separate, disposable browser profile/origin**, only after safeguarding original data; not necessary to count the present same-data smoke test as successful.
- Clarify whether future player guide should include an explicit update-and-backup tutorial.
- **Checkpoint contamination question remains an ongoing methodological caution:** pauses are acceptable, but classify later interactions as coached or regression tests when that is what they are.

## Provenance note

This record distinguishes **user-reported local observations** from **GitHub-confirmed merges** and **interpretation**. It is a concise reconstructed checkpoint, **not** a verbatim transcript, complete record of all earlier conversations, or a claim of independent remote access to the user's Bazzite computer.
