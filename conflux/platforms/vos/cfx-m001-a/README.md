# CFX-M001-A — Simulated VOS State Service

Experimental prototype implementing the frozen CFX-M001-CONTRACT-v1.0 `/state` and `/health` endpoints. Python 3 standard library only; simulated values, no hardware access.

## Start on Bazzite / Linux

```bash
python3 vos_state_service.py
```

In another terminal:

```bash
curl http://127.0.0.1:8080/state
curl http://127.0.0.1:8080/health
```

Stop with **Ctrl+C** in the service terminal. It does not install itself, modify the OS, or start automatically. It binds only to 127.0.0.1. If port 8080 is occupied, use `--port 8081` and adjust the curl commands accordingly; the frozen contract baseline remains 8080.

## Scope and limits

- New UUID per process start; sequence starts at 1 and advances every 500 ms.
- Repeated GET requests may return the same sequence, as required by CR-03.
- `/health` confirms the service responds; it is **not** independent supervision.
- Does not implement the client, test harness, independent watchdog, or host recovery.
- No test results are asserted in this package. Specula audit remains pending.
