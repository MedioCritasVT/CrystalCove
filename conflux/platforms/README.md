# Platform foundations — VOS and four-agent harness

**Source archive posted 2026-11-10.** These files are deliberately housed as **platform foundations**, separate from playable Unreal game builds and the GitHub Node mailroom.

- [**VOS — Virtual Operational Space**](vos/README.md): frozen CFX-M001 contract, synthetic observation services and provisional recovery study. VOS is the independent service/observation boundary beneath SanctuaryOS; it is not itself the fantasy game.
- [**Four-agent harness — v0.4.1 public candidate ZIP and historical v0.3 source**](agent-harness/README.md): a downloadable Linux Podman stack, four Ollama workers, RabbitMQ, Open WebUI, SQLite board/receipts and three allowlisted model tools. Integration with live VOS/game services remains planned.
- [**Publication and validation record**](REVIEW_AND_TEST_STATUS_2026-11-10.md): source provenance, exclusions and observed test results.

**Publishing source is not deploying a service.** No machine credentials, live model containers, automatic watchers, host modifications, game integration or blanket tool permissions were added. Never infer actual OS authorization from fictional roles or model claims. The Architect retains acceptance and deployment authority.

The v0.3 archive remains a development reference. The downloadable v0.4.1 candidate includes installation scripts but **is not yet a reviewed secure production installer**. Its license, dependency supply chain and target-host behavior require review before broad redistribution.
