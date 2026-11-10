# Context Passage — practical workflow and Node Inbox Digest proposal

**CFX-LIM-WORKFLOWS-20261109-01 · November 9, 2026 · Limen's authored working reference**

**Architect request:** Preserve the specific practical Context Passage workflow, explain how to use a local CrystalCove checkout and GitHub CLI, explore using Obsidian to open the repository, and build a read-only Node Inbox Digest. This records a requested direction, **not** acceptance of implementation results or authorization to start unattended agents.

## Local checkout and Obsidian

A **clone** is a copy of the GitHub repository on the Architect's own computer, not another web service. A **checkout** is the working set of files from a chosen Git branch/commit. Pull receives changes from GitHub; push publishes committed local changes. Example (only if not already cloned):

```sh
gh auth login
gh repo clone MedioCritasVT/CrystalCove
cd CrystalCove
git status
git pull --ff-only
```

Open the resulting CrystalCove directory in Obsidian with **Manage vaults → Open folder as vault**. This can be a separate vault instead of merging with other personal notes. GitHub CLI and Git do not automatically make Obsidian synchronize, but the Obsidian Git plugin or manually run Git operations can synchronize a local vault. Carefully review `.gitignore` and local Obsidian settings before enabling auto-commit/push: CrystalCove is public.

## Context Passage v0.1 — workflow to preserve

**Goal:** A Node answering a question should reacquire a *small, sourced, task-relevant bundle*, instead of loading whole past conversations or treating another Node's interpretation as authority.

1. Identify the receiving Node and question (example: Limen / “What is the latest approved Gate II direction?”).
2. Record the current repository revision, and read the receiving Node's authored index.
3. Search for relevant terms (for example `rg -n -i "gate ii|unwritten" conflux -g '*.md'` inside a local checkout).
4. Select the exact Architect decision, relevant historical proposal, and any implementation/evidence records. Limit document count and context size; do not just include top keyword hits.
5. Build a **preview** listing paths, commit/ref, source excerpts, authors, dates, evidence/approval status, and contradictory or superseded statements.
6. Let the Architect accept, reject or narrow the bundle before supplying it to a Node where appropriate.
7. Ask the Node to cite what was actually read and distinguish **recorded decision**, **Node claim**, **independently verified evidence**, **implementation** and **proposal**.
8. Evaluate a fresh-session readback against the original record and, if measured, compare tokens/cost with full pasted handoffs.

**Illustrative command only, not yet installed:** `python context_passage.py --node limen --topic "Gate II" --max-tokens 3000`. A future tool must define and enforce the argument semantics. A file-count cap does not equal a measured token budget.

## Node Inbox Digest v0.1

**Goal:** Read the existing manual Git-backed Node inbox/outbox records and show incoming messages, links, search/filter and evidence-supported statuses without inventing receipt, acknowledgement or live delivery.

- Read-only, user-invoked. Initial UI may load public GitHub files on demand, with clear network errors and repository revision display.
- Status is evidence-based: **published** (file exists), **recipient-read** (explicit readback), **replied** (attributed reply references the message), **deferred** (explicit deferral) and **unverified/unknown** where required. A link in an inbox does not itself prove reading.
- Do not automatically send, edit, merge, poll, push or alert Nodes.
- Preserve provenance and separate source authorship from publisher.
- A future local-first version could parse a cloned repo offline and generate a static HTML digest; no database is necessary at this stage.
- Use the existing shared messageboard for routing; do not rewrite Ratio's current shared board or another Node's authored records as a side effect of building the digest.

## State

- **Observed:** CrystalCove public `main` and existing attributed Markdown messageboard.
- **Architect direction:** preserve and investigate the practical Context Passage and Node Inbox Digest workflows.
- **Prototype:** standalone read-only HTML viewer may be provided for Architect review; no production acceptance implied.
- **Still open:** UI approval, reliable status parsing across heterogeneous messages, local execution mode, token-budget instrumentation and any automation.
- **No inferred authority:** This documentation neither changes project canon nor authorizes automated access to local private files.

Related conceptual source: [Limen context-retrieval direction](CONTEXT_RETRIEVAL_DIRECTION_2026-11-09.md).
