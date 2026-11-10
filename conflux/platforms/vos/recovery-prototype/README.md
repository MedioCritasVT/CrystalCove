# VOS observation-layer proof of concept — provisional

Python standard library only. Tested on hosted Linux; Python 3.10+ recommended. No host desktop integration, real sensors, engine, GUI atmosphere, networking or external service is used. The renderer is a subprocess producing a JSON display projection, a replaceable stand-in for a graphical renderer.

## Reproduce

Extract this ZIP and open a terminal in its `vos` directory:

```sh
python3 -m unittest -v test_contract
python3 check_mutations.py
```

The first command exits nonzero when any contract assertion fails. The second introduces three deliberate defects into temporary copies and succeeds only if each corresponding gate rejects its defect. Logs are written to `evidence/`; copy that directory first if you want to retain the supplied run unchanged. `MANIFEST.sha256` describes the supplied files; rerunning changes the evidence hashes.

## Components

- `state.py`: state authority, receipt-freshness timer and explicit challenge/session handshake. Duplicate/regressed sequence or unknown session is a no-op. Retired sessions cannot be reused during the state object's lifetime.
- `runtime.py`: independent watchdog process owns primary and renderer subprocesses. Primary simulates sensor readings and writes upstream truth even when renderer is dead. Watchdog observes heartbeat gaps and process exit independently; stalled upstream truth becomes unknown, rather than remaining falsely present.
- `test_contract.py`: real SIGKILL renderer injection, real unresponsive-primary loop, and deterministic controlled-clock replay tests. The parent test process initiates faults and asserts observations; the watchdog performs primary recovery without commands from the parent.
- `check_mutations.py`: checks that hiding renderer loss, disabling watchdog timeout, or resetting freshness on duplicate packets makes its gate fail.

Atomic local JSON files provide IPC. `state.json` is upstream sensor truth, `display.json` is renderer output, `health.json` is watchdog health interpretation, and `supervisor.jsonl` records transitions. A dead renderer intentionally leaves its last display file; consumers must use independent health rather than interpreting that file as live output.

A sensor becomes missing after 0.3 seconds without an accepted sample. A primary heartbeat gap over 0.6 seconds triggers SIGKILL, wait/reap, new primary process, and explicit new-PID readiness heartbeat. Recovery is reported only after that heartbeat. Each scenario has a bounded test timeout and subprocess cleanup.

## Deliberate boundaries

Receipt-freshness is not acquisition-freshness. A new sequence carrying an old source timestamp is accepted and explicitly reports acquisition age unknown. Rejecting all such packets would require a separate trusted acquisition-time or request/response policy. The handshake here is an in-process protocol model, not authenticated transport; primary initializes a fresh state instance on restart. Replay protection across authority restart, persisted session history, malicious senders, schema hardening and sequence exhaustion are not solved.

The independent watchdog itself is not supervised by an external host service. It publishes a heartbeat, but watchdog death detection and recovery are unverified. Filesystem failure, clock-source failure, heavy-load behavior, retry storms, and simultaneous faults are not demonstrated. This is a single-host development prototype, not a supported Bazzite baseline.

The OS-owned manual escape hatch remains UNVERIFIED and is not implemented or coupled to recovery. Killing/restarting primary_path does not establish desktop recovery or an escape hatch. No user PC settings were accessed or modified.
