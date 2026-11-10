# Platform source publication and validation

**Date:** 2026-11-10  
**Publisher:** Limen, on Architect request  
**Disposition:** **source archived; runtime/production acceptance NOT granted**.

## Archived inputs

- `CFX-M001-CONTRACT-v1.0.md` — preserved frozen contract, unchanged.
- `CFX-M001-A-prototype.zip` — README and Python simulator.
- `vos_observation_0_1.zip` — simulator and test source.
- `VOS_Prototype_Evidence.zip` — README and selected process/state/test source; machine-specific evidence and logs **omitted**.
- `Conflux-VOS-Harness-v0.3.zip` — complete textual source/launcher/README tree; **no passwords or local runtime configuration**.
- `VOS_Harness_Integration_Plan_2026-10-30.md` — dated planning reference only.

Source text was copied without feature rewrite. Static pattern checks found no embedded secrets, private home paths or personal identities in the selected files; this is **not a security audit**.

## Tests run in this publication session

| Test | Actual outcome | What it establishes |
| --- | --- | --- |
| Observation 0.1: Python unittest | **4/4 passed** | Deterministic synthetic sensor behavior |
| Recovery prototype: Python unittest | **1/3 passed; 2 failed** | Replay check passed; renderer-loss and primary-watchdog integration assertions failed in this environment |
| Four-agent v0.3: `test_vos.py` | **Blocked** | `ModuleNotFoundError: No module named 'pika'`; cannot claim tested success here |

The original recovery archive reported 3/3 tests passed on October 25, 2026. That **conflicts** with this fresh rerun and is retained as earlier attributed evidence rather than treated as verification here. No archived code was patched to manufacture a passing test.

No real sensors, host supervisor/recovery, external APIs, game telemetry, live containers, authorized operating-system privileges, or production security were verified in this pass.

**Before any future deployment:** locate the authoritative frozen contract, reproduce tests in an agreed environment, review credentials and least-privilege boundaries, and request explicit Architect authorization.
