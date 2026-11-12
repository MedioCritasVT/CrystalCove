# Four-Agent Harness — v0.4.1 Public Release Candidate

**Status: review candidate; NOT a published download or merged feature.**
**Proposed home:** `conflux/platforms/agent-harness/v0.4-public/`; preserve historical `v0.3/` files.
**Package:** `4AgentHarness_CrystalCove_Public_v0.4.1.zip` (50,924 bytes)
**SHA-256:** `961929174a824f7d0615c2f0d8f04b53f00f16bc4f7c22fc061783d0492ed832`

The candidate ZIP has been prepared separately and requires publication to an actual repository directory or release asset before anyone can download it from GitHub. This file **is not** a claim that the package has been uploaded to GitHub.

## What's packaged

- Four separate Podman agent workers (Qwen3.5 4B/9B defaults), shared Ollama, Open WebUI, RabbitMQ, controller.
- Existing SQLite shared notes and tool receipts; existing bounded `post_note`, `read_notes`, and `ask_node` tools.
- A new **operator-only read-only SQL inspector** (`./sql.sh`), separate from model tools.
- In-memory SQLite FTS5 demonstration, not a live RAG index.
- A sanitized example of the MedioCritas persona prompt and model settings; no account IDs or image payloads.
- Documentation for SQL vs RabbitMQ vs Git vs RAG, two-agent inference parameters, and future VOS/game integration.
- No embedded Ollama weights, secrets, private shared-board records, Open WebUI account data, or live game credentials.

## Important architectural distinction

- **RabbitMQ:** queues / RPC / change notifications, not a durable searchable knowledge corpus.
- **SQLite + future FTS5:** versioned local records and source-grounded retrieval; current board is shared, private agent memory is **not** implemented.
- **Git:** authoritative code and approved document versions; it does not replace memory isolation or live runtime evidence.
- **Future bounded gateway:** an explicitly reviewed interface to read-only VOS observations and Unreal game events. **Not connected in this release.**

## Verification and release gates

- Packaging-level checks: 16 local mocked/SQL tests passed; Python and shell syntax checked; ZIP integrity checked.
- Still required: live Podman/Ollama/Open WebUI/RabbitMQ/GPU acceptance testing on a target computer, review of code/licensing and reproducibility.
- The current CrystalCove repo had no root LICENSE file when inspected. Select a license and review the dependencies before inviting broad redistribution.
- Do not merge this planning note as proof the installer is hosted. Attach/upload the candidate ZIP and source first, confirm checksum and working links, then update the public platform index and portal.

## Integration references

- [Historical agent harness](v0.3/README.md)
- [VOS–Harness–Game integration plan](../vos/VOS_Harness_Integration_Plan_2026-10-30.md)
- [VOS service foundation](../vos/README.md)

**Approval boundary:** Packaging is authorized for review. This candidate does not approve production deployment, private-memory database migrations, agent permission expansion, or changes to the Unreal game.
