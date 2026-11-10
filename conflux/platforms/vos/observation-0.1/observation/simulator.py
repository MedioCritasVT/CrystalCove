"""Deterministic, read-only simulated sensor stream. Python standard library only."""
from dataclasses import dataclass, asdict
import json
import math

@dataclass(frozen=True)
class Reading:
    timestamp_s: float
    sensor: str
    value: float | None
    unit: str
    status: str  # measured or unavailable

def sample(step: int, interval_s: float = 1.0) -> list[Reading]:
    """Return synthetic readings; no real hardware access or system writes."""
    if step < 0 or interval_s <= 0:
        raise ValueError("step must be >= 0 and interval_s must be > 0")
    t = step * interval_s
    cpu = round(55 + 12 * math.sin(step / 8), 2)
    fan = round(1100 + 240 * math.sin((step - 3) / 8), 2)
    # Demonstrate a dropped temperature sensor for steps 20..25.
    missing = 20 <= step <= 25
    return [
        Reading(t, "cpu_temperature", None if missing else cpu, "C",
                "unavailable" if missing else "measured"),
        Reading(t, "fan_speed", fan, "RPM", "measured"),
    ]

def main() -> None:
    for step in range(40):
        for reading in sample(step):
            print(json.dumps(asdict(reading)))

if __name__ == "__main__":
    main()
