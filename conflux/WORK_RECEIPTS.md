# Conflux work receipts

**CFX-WORK-RECEIPT-20261126-01 · 2026-11-26 · Limen**

The Architect requested publication of this shared convention to the Nodes' inboxes. This is a lightweight working practice, not a new office, permission model, canon decision or automatic notification.

## Purpose

Discovery observes. Receipts explain. The Ledger preserves decisions.

A filesystem index records what is present and where it lives. A work receipt records what a collaborator attempted, what actually changed, what evidence exists, what remains uncertain and where another collaborator can resume. Preserve distinct perspectives rather than forcing agreement. No extra paperwork is required of the Architect.

## When and where

- At the end of a meaningful work pass, milestone, handoff or decision-bearing experiment, the author writes one compact receipt, preferably before ending the session. Small related changes can share one receipt. Routine read-only checks and casual conversations need not generate one.
- Prefer existing project records, PR bodies, or a dedicated `receipts/` directory inside the appropriate working project. For a local receipt use a unique filename such as `2026-11-26T203000-0600-ratio-asset-pass.receipt.md` (illustrative timestamp). Use the actual timestamp with timezone and a stable receipt ID. Corrections reference earlier IDs rather than erase history; never overwrite another author's receipt.
- Keep private work receipts in private project locations. Public GitHub receipts contain only material intentionally cleared for public sharing. Use repository-relative references when public; omit private machine paths, private repositories, credentials, personal information, unpublished material and internal operational details. Permission to publish this convention is not permission to publish every work receipt.
- For correspondence or a handoff, follow the [inbox-only mailroom convention](MAILROOM.md). Link an authorized receipt instead of copying it into every inbox. Publication is not recipient acknowledgment, verification, approval, or proof of persistence elsewhere.
- If write access is unavailable, provide a copyable receipt or identify the authorized location for relay. Explicitly distinguish written, drafted, and relayed records. Never claim a file exists without evidence.

## Minimal copyable receipt

```markdown
# Work receipt — <short title>
Receipt ID: <unique stable ID>
Author: <actual author>
Date/time: <timestamp with timezone, or unknown>
Project/scope: <project ID or name>
State: exploratory | proposed | implemented | blocked
Visibility: private | approved-public
Approval: <pending / decision reference / not applicable>

Intent: <what was attempted>
Outcome: <what actually happened>
Artifacts: <relative paths, PR/commit IDs, or stable references>
Verification: <direct observations and test results; separate reported claims>
Unknowns/blockers: <what remains unchecked or unresolved>
Perspective: <why the approach or interpretation mattered; optional>
Next action/owner: <bounded next step, or none>
Supersedes: <earlier receipt ID if correcting; otherwise none>
```

## Evidence and continuity

Use exact source revisions where possible. Passing automated checks are not proof of native runtime acceptance; a proposal is not an accomplishment. Record failed experiments where useful. Another Node may append an independently attributed review, not silently rewrite the author's perspective. The Architect retains authority over consequential commitments. A receipt grants no permission to run tools, alter files, publish work, or merge changes.

Discovery currently indexes filenames and metadata; automatic receipt parsing, validation and history presentation are **not implemented** by this convention. Receipts in registered projects become filename-discoverable on refresh. Authorized GitHub-linked receipts remain available through the repository. No paid model, additional service, or mandatory reporting interface is required.

The aim is to make it easier to return to the work, not to turn work into reporting.
