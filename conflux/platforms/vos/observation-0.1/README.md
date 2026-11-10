# VOS Observation Layer — 0.1 sensor simulator

First brick: a deterministic simulated sensor stream, **not** real telemetry.
No third-party packages, root access, hardware access, or OS changes required.

## Run (from this folder)
```bash
python3 -m observation.simulator
```
Each output line is JSON with timestamp_s, sensor, value, unit, status.

## Test
```bash
python3 -m unittest discover -s tests -v
```

The CPU temperature stream intentionally becomes unavailable at steps 20–25.
Fan speed continues independently. At step 26, temperature resumes.
The simulator reports missing data as `null`, never a stale reading.
This file is the sensor source only: timeout thresholds, environmental fades,
visualization, and real hardware integration are future components.
