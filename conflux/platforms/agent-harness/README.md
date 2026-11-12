# Four-agent harness — local distribution and archive

## Download v0.4.2 — 9B primary, 4B support agents

**[Download the updated four-agent harness ZIP](releases/4AgentHarness_CrystalCove_Public_v0.4.2.zip)** · [Import MedioCritas 9B through the VOS Pipe](MedioCritas_VOS_9B_import.json)

The v0.4.2 candidate defaults to **Node 1: qwen3.5:9b** and **Nodes 2–4: qwen3.5:4b**, sharing a single Ollama service. The Pipe exposes three bounded tools: `post_note`, `read_notes`, and `ask_node` through the existing SQLite/RabbitMQ controller.

**Existing v0.4/v0.4.1 installation:** do not re-run the new installer. Extract the ZIP elsewhere, then preview and apply the bundled upgrade script with the path to your **existing** project:

```bash
./upgrade-model-routing.sh --target /path/to/existing/4AgentHarness
./upgrade-model-routing.sh --target /path/to/existing/4AgentHarness --apply
```

The second command backs up the existing agent `.env` files and recreates only workers whose model assignment changes. It does not remove named Podman volumes, SQL data, RabbitMQ state, or Open WebUI accounts. The importable VOS model JSON uses a **new model ID**, so a direct Qwen 9B MedioCritas persona need not be overwritten.

**Validation:** local mock tests and packaging checks, not an AtticOS deployment test or production certification. Confirm real worker environment values, successful inference, and actual tool receipts after applying the update. Private per-agent memories, live RAG, VOS services, and the Unreal bridge remain future integration work. An explicit project software license remains unresolved.

---


## Previous download (v0.4.1) — retained for compatibility

**[Download the complete v0.4.1 ZIP](https://raw.githubusercontent.com/MedioCritasVT/CrystalCove/main/conflux/platforms/agent-harness/releases/4AgentHarness_CrystalCove_Public_v0.4.1.zip)**

- **50,924 bytes** · SHA-256 `961929174a824f7d0615c2f0d8f04b53f00f16bc4f7c22fc061783d0492ed832`
- Designed for Linux + Podman + Ollama + Open WebUI + RabbitMQ, with four agent containers and a shared SQLite note board.
- Operator-only read-only SQL inspection and example model parameters are included. Private agent memories, live RAG, VOS service integration, and Unreal-game integration **are not part of the deployed feature set**.
- Setup notes and executable scripts are inside the ZIP. Preserve existing volumes and back up user configuration before changing a running installation.
- **Validation:** local mocked tests/packaging checks, not a cross-machine production certification. An explicit public software license is still needed before broad redistribution.

[Publication record and limitations](PUBLIC_RELEASE_CANDIDATE_v0.4.1.md) · [VOS/game integration planning](../vos/VOS_Harness_Integration_Plan_2026-10-30.md)

## Preserved historical source (v0.3)

**Status: preserved local prototype, not currently deployed or independently accepted by this publication.**

[Browse the v0.3 source and original README](v0.3/). The archived source includes `coordinator.py`, `transport.py`, `openwebui_vos_pipe.py`, `test_vos.py`, `Containerfile` and `vos.sh`.

The four-worker harness was built for an existing local Ollama/Open WebUI + RabbitMQ + Podman setup. Its SQLite board tracks notes and execution receipts. Only three bounded model tools are provided:

| Tool | Scope |
| --- | --- |
| `post_note` | Write a bounded attributable text note |
| `read_notes` | Retrieve a bounded set of notes |
| `ask_node` | Make one non-recursive peer request |

This is a **four-worker technical experiment**, not proof of five active Conflux Nodes, not the GitHub forum, and not a general autonomous agent or host-execution harness. The archived script is **not** a fresh-install package; it can start or connect existing local containers and requires local credentials. Do not run the launcher or publish its interfaces just because it is available as source.

The original README reports limited mocked tests. In this publication environment, a new harness test run could not import the missing `pika` dependency; no passing live test was claimed. See the [publication record](../REVIEW_AND_TEST_STATUS_2026-11-10.md).

Future integrations need separately approved permissions, source-provenance and service-ownership contracts; no model can promote its own suggestion into system authority.
