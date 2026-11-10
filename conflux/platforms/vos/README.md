# VOS — service and observation foundation

**Status:** archived prototypes and immutable design reference; no live host telemetry or complete VOS OS layer is established by this publication.

| Source | Function | Boundary |
| --- | --- | --- |
| [CFX-M001-CONTRACT-v1.0](contracts/CFX-M001-CONTRACT-v1.0.md) | Frozen simulated observation service contract | Preserve unchanged; verify authoritative version before integration |
| [CFX-M001-A prototype](cfx-m001-a/README.md) | Python local loopback `/state` and `/health` | Synthetic CPU/fan values only; no real host sensors |
| [Observation 0.1](observation-0.1/README.md) | Deterministic independent sensor stream and tests | No live hardware access |
| [Recovery proof of concept](recovery-prototype/README.md) | Experimental watchdog, renderer loss, freshness/replay handling | Process-level demonstration; **not** operating-system recovery or manual escape hatch |
| [October 30 integration plan](VOS_Harness_Integration_Plan_2026-10-30.md) | Articulated integration sequencing | Planning document only |

VOS must allow independent troubleshooting of services and diagnostics. SanctuaryOS can later use trustworthy observations to render atmospheric machine weather (clear/mist/fog/storm), but this source archive does not implement that experience. **“Control instruments, never the sky.”** The Attic globe and refresh balloon remain design proposals.

Machine-specific evidence and log snapshots in the original recovery ZIP were intentionally not copied to this public tree. The included original README may point to those excluded files. The [test note](../REVIEW_AND_TEST_STATUS_2026-11-10.md) records fresh test failures, so do not call the recovery prototype accepted or verified.

There is no approval here to grant system privileges, expose HTTP endpoints to the internet, start supervisors, install services, or modify the Architect's host.
