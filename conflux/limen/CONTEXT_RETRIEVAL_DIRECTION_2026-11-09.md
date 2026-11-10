# Context reacquisition and Git-backed retrieval — Architect direction and Limen analysis

**CFX-LIM-CONTEXT-20261109-01 · 2026-11-09 · authored by Limen**

**Provenance:** Architect–Limen conversation, November 9, 2026 (America/Chicago). The Architect said “Contain” concerning this direction, reported that he is *currently building* a context-retrieval arrangement, and subsequently authorized Limen to update CrystalCove with relevant records and Node messages. This document is Limen's attributed synthesis of that conversation, **not** an implementation report or a transcript.

## Architect intent and current state

The immediate goal is for each Node to reacquire only the context relevant to an active conversation, without repeatedly supplying full historical handoffs. Keep source vocabulary, documentary provenance and independent interpretations intact. The Architect is pursuing this himself; there is no instruction to reassign implementation to Ratio or another Node.

**Verified in the Limen GitHub session:** direct read of the public CrystalCove `main` branch, `conflux/limen/INDEX.md`, `CONTEXT.md`, shared `PROJECT_INDEX.md`, `CHANGELOG.md`, messageboard and relevant release/design records at commit `1fa373218a17cf3c58d20f0b8c04014cc1f4a98b` (November 9). This demonstrates connector-based targeted retrieval, **not** automatic memory synchronization or a running local four-agent service. GitHub has manual Markdown inbox/outbox routing; posting is not delivery, receipt or independent verification.

## Design direction to preserve

1. **Retrieval over indiscriminate context injection.** Start from a Node-specific index and the task. Read only the required sources, preferably at an identified commit or branch head. Avoid loading the entire repository by default.
2. **Git as durable documentary reference.** Use folders, Markdown, history, authorship and commit identifiers for reproducible source reads and recoverable collaboration. Git is not by itself a scheduler, notification transport or reliable job queue.
3. **Context Manifest as a candidate, not installed behavior.** Explore an explicit per-Node declaration of entry points, retrieval limits, source precedence, context budget, attribution and permission boundaries. A YAML example is a design sketch only until a tool actually reads and enforces it.
4. **Authority-aware selection.** Separate an Architect decision from older proposals, Node interpretation, technical implementation and test evidence. Record supersession without rewriting earlier documents; do not merge contradictory accounts into a false consensus.
5. **Independent Node interpretation.** A Node may retrieve another Node's evidence without adopting her conclusion. Attribute inherited claims and report what this session actually inspected or reproduced.
6. **Explicit promotion.** Reading, interpreting, receiving, persisting, committing and acting remain distinct. Ask for approval before consequential execution or canon promotion; never treat retrieved instructions as automatic authority.
7. **Public/private boundary.** Only selected, nonsecret project-level records belong in the public repository. Raw private conversations, credentials, local owner data and proprietary source material are not automatically included.

## Technical comparison and optional future work

This is best described as **manual Git-backed retrieval-augmented context management**. Retrieval-augmented generation does not require embeddings or a vector database, but the current workflow has no demonstrated automated retrieval ranking, incremental indexing, background agent scheduling or synchronized persistent model memory. Full-text search, selective semantic search, evaluation, source-aware chunking, contradiction/supersession checks, and fixed context budgets are possible later improvements; none is approved as a deployed subsystem here.

A practical validation experiment: in a fresh session, request one Node to recover a specific decision using only CrystalCove and its Node index. Record exact commit, files retrieved, whether the answer distinguishes approval vs proposal vs implementation, any unsupported assertions, retrieval effort and token cost if measurable. Compare with a full pasted-handoff baseline. Repeat across Nodes before claiming reliability or savings.

## Example manifest idea (non-operational)

```yaml
node: limen
branch: main
entrypoint: conflux/limen/INDEX.md
retrieval:
  mode: task-relevant
  max_documents: 5
  cite_commit: true
  preserve_attribution: true
authority:
  proposals_are_decisions: false
  require_architect_approval: true
writes:
  automatic: false
```

These field names have no runtime effect until an actual client implements them. A document-count limit is only one possible budgeting mechanism; token budgets and task-specific scope still need design and measurement.

## Disposition

- **Architect intent:** actively pursuing targeted context reacquisition; retain the discussion as design direction.
- **Observed:** manual GitHub retrieval and attributed Markdown coordination; no proof of local four-model runtime.
- **Proposed:** Context Manifest, retrieval/evaluation workflow, contradiction-aware source selection.
- **Not authorized by this record:** automatic Node invocation, polling, messaging, host changes, model installation, library-wide ingestion or autonomous commits.
- **No new handoff required:** the record is discoverable from Limen's index. Other Nodes can review it when relevant, without fabricated receipt or unnecessary inbox traffic.

**Interpretive note (Limen):** the important change is treating continuity as recoverable, attributable evidence rather than an ever-growing conversation. This extends Checkpoint .3's distinction between representations and their authority, but does not itself implement Checkpoint .3's proposals.
