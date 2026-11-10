# VOS Services × Four-Agent Harness × Game — Integration / Merge Plan

**Directive from Architect, October 30, 2026:** Document orchestration and progress sharing should belong to **VOS services and the four-agent harness**, unless a carefully reviewed merger of project files **and functionality** can serve both better. **Status: architecture proposal and handoff organization only. No implementation or modification authorized.**

## Present, separately grounded components

| Component | Evidence | What it does / does not do |
| --- | --- | --- |
| CFX-M001 contract | Frozen `CFX-M001-CONTRACT-v1.0.md` | HTTP loopback `/state`, `/health`, sequence and freshness rules, error categories; baseline is read-only and **must not be edited in place** |
| Simulated VOS service A | `CFX-M001-A-prototype.zip` | Python local fake telemetry generator; no host sensor data or privileged control; `/health` is not independent supervision |
| Four-agent harness v0.3 | `Conflux-VOS-Harness-v0.3.zip` | Four Ollama workers via RabbitMQ; Open WebUI pipe; controller tool allowlist `post_note`, `read_notes`, `ask_node`; SQLite shared board and receipts; no live VOS status tool; not unrestricted execution |
| Sanctuary browser candidate | `Conflux-Medio-Canonical-Visual-Polish.zip` | Standalone Three.js fictional game, source assets, realm/Node behavior, keyword situations; **no** live VOS, AI, host permissions, recovery supervisor or Unreal interface |
| Documents and Visuals | Provenance/visual archive | Versioned handoff material, **not** live runtime configuration or authorization |

## Long-term conceptual data flow (not implemented)

```text
Bazzite host / OS controls / OS-owned escape and independent supervisor
       |                            | (remains out of band)
       v                            v
VOS telemetry producer -----> independent validator / freshness client
             [frozen contract]    [VALID/STALE/MISSING/INVALID/
                                   SERVICE_UNAVAILABLE/RENDERER_UNAVAILABLE]
                                      |
                      validated, minimal read-only observation projection
                                      |
                +---------------------+---------------------+
                |                                           |
       VOS services diagnostics                        bounded harness reader
        (immutable event source +                     (future *proposed* tool;
         human-readable reports)                       explicit allowlist/receipts)
                |                                           |
                +---------------------+---------------------+
                                      |
                     optional game / Unreal world renderer
                     (presentation, no permission authority)
                                      |
                            user decides/refuses/undoes
                                      |
                       explicit authorization gate for
                        any future real write operation
```

**Critical distinction:** neither the four-node model's confidence nor the renderer's visual status can reclassify validator results or approve a host action. The independent watchdog/escape must not be an overlay or chat tool. Use client-monotonic receipt of a *new* validated sequence to govern freshness; unchanged sequence does not reset the timer; retired instance IDs require guarded revalidation. Render errors remain separate from service errors.

## Document orchestration as VOS/harness service, eventually

The desired shared coordination index would track `artifact_id`, version, SHA-256, source, owner/Node, authoritative origin, status (`PROPOSAL`, `APPROVED_DESIGN`, `IMPLEMENTED`, `TESTED`, `REJECTED`, `DEFERRED`), related frozen contract, and rollback/recovery location. **This packet is a static exemplar**, not a working service/database migration. A record must distinguish actual tool receipts and human approval from generated claims.

**Future optional tooling, requires review:** bounded `list_artifacts`, `read_artifact_manifest`, `read_vos_state_snapshot`, `record_handoff_receipt` and `propose_change` (proposal only). Each operation needs its own input validation, access policy, data minimization, provenance, audit record and denial tests. These tools are not in v0.3; do not claim they exist or add them by changing a model prompt.

Existing `post_note`/`read_notes` may carry a manually relayed concise pointer to this archive. **Do not send the entire literary manuscript, private user records, passwords, or large archives to the shared board.** The board is persistent across the local harness, shared among nodes, and **not a privacy barrier** between untrusted users.

## Merge decision: separate repos now, modular monorepo later?

**Conservative recommendation:** begin with a common **documentation/manifest namespace** while leaving the source archives and runtime boundaries intact. A future reviewed repository could contain:

```text
conflux/
  docs/            # Codex, ledger, architecture, provenance, Book 5 handoff
  services/vos/    # state service, validation, independent diagnostics
  harness/         # bounded controller, Ollama nodes, event/receipt ledger
  clients/         # independent validated status clients and test harnesses
  game/browser/    # replaceable offline learning prototype
  game/unreal/     # eventual engine path, not yet asserted as working
  art/             # versioned references and licensing/usage records
  tests/           # contract, integration, outage/freshness, and UI tests
```

**Moving files into one folder or Git repository is not integrating functionality.** Functional merger is only appropriate when dependencies, security boundaries, data flows, updates and rollback are tested. Avoid wiring a web game directly to `127.0.0.1:8080` and assuming that validates host, auth, lifecycle or origin policies. Container networking, cross-origin rules, service identities and Bazzite recovery remain open engineering questions.

## Proposed gates — no steps authorized by this planning packet

**Gate 0 — inventory/provenance:** review versions and hashes; identify canonical repo and source-owner approvals; verify current Bazzite containers; remove secrets from shared material. No runtime change.

**Gate 1 — read-only validator and diagnostics:** independent freshness client tests CR-01/02/03 against simulations, forced stale/restart/absence/bad JSON; separately reliable OS-owned escape/supervision design. Ensure human-readable report folder and structured append-only evidence.

**Gate 2 — optional harness read adapter:** approved, testable, allowlisted read-only snapshots with provenance; never elevate tools to shell/host control merely for agent convenience; use a separate namespace from chat notes.

**Gate 3 — graphical consumer:** game receives a sanitized observation layer and displays uncertainty truthfully; independently prove screen/renderer failure and return-to-desktop behavior. Never let gameplay gates control genuine permissions.

**Gate 4 — coherent packaging/merge:** only after gates above and explicit Architect approval, consider a shared source tree, versioned migration, CI tests, safe secrets handling, backup and rollback. Browser replacement with Unreal is a planned direction, not accomplished.

## Nexus coordination handoff

Nexus can **index**, identify gaps, coordinate separate node reviews, propose experiments and maintain records. The Architect approves any code change, permission expansion, deployment, publishing or release. Specula reviews observable claims and failure evidence; Ratio checks mechanics; Medio protects lived experience and grace; Limen checks translations and boundaries. No node's office substitutes for the approval gate.

**Do not merge or deploy until the Architect chooses a bounded scope.**
