# Four-agent harness — v0.3 archival source

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
