# CFX-M001 Interface Contract — v1.0 (FROZEN)

**Status:** FROZEN — CFX-M001-CONTRACT-v1.0. Immutable baseline for Milestone 001.  
**Incorporates:** LIMEN-TR-002, SPECULA-AR-002, LIMEN-AR-003 (CR-01, CR-02, CR-03).  
**Authority:** Architect-supervised. Frozen after Node verification.  
**Date frozen:** 2026-10-25  
**Note:** No implementation has begun. A/B/C may now proceed to bounded EXPERIMENT.  

## 1. Transport & Endpoints
- Protocol: HTTP/1.1 over local loopback (127.0.0.1)
- Base URL: http://127.0.0.1:8080
- Endpoints:
  - GET /state — Returns the current structured telemetry payload.
  - GET /health — Returns basic service liveness and instance metadata.
- Client HTTP timeout: 1,000 ms (experimental; shorter than stale threshold).
- Error responses: Connection refused, timeout, or non-2xx → SERVICE_UNAVAILABLE. Malformed JSON or schema violation → INVALID.

## 2. Payload Schema (schema_version: "0.1")

```json
{
  "schema_version": "0.1",
  "source": "vos-simulator",
  "service_instance_id": "uuid-v4-string",
  "sequence": 1042,
  "timestamp": "2026-10-25T22:00:00Z",
  "monotonic_elapsed_ms": 125400,
  "cpu_temperature_c": 54.2,
  "fan_speed_rpm": 1280,
  "state": "nominal"
}
```

**Required fields:** schema_version, source, service_instance_id, sequence, monotonic_elapsed_ms, state.  
**timestamp:** wall-clock diagnostic metadata only.  
**monotonic_elapsed_ms:** Service diagnostic and continuity check only. Not used for cross-process freshness comparison.  
**Telemetry fields:** optional for first experiment but must validate if present.

## 3. Session-Transition & Sequence Rules (CR-01, CR-03)

**CR-01 — Session transition**  
- A new service_instance_id triggers session revalidation.  
- It does not automatically establish that the new stream is trustworthy.  
- Previously retired instance identifiers must not silently regain active status.  
- Clean restart (new instance ID, sequence reset) is recognized only after revalidation succeeds (TC-RESTART-01).

**CR-03 — Polling and sequence semantics**  
Because the service generates telemetry every 500 ms and the client polls every 250 ms, consecutive successful responses may legitimately contain identical sequence numbers.  
The client must:  
- Accept an unchanged sequence as the same previously validated reading, without refreshing its freshness timer.  
- Accept a strictly increasing sequence as a new reading and refresh the freshness timer.  
- Reject a decreasing sequence as a regression (INVALID).  
- Reject conflicting payload contents presented under the same instance ID and sequence number (INVALID).  
An identical response is not automatically evidence of a replay attack.

## 4. Freshness Authority (CR-02)
Client-side freshness calculations must use the client's own monotonic clock and the receipt time of the last newly validated reading.  
The service's monotonic_elapsed_ms is useful for service diagnostics and continuity checks but must not be directly compared with a different process's monotonic clock.  
Wall-clock discontinuities must not affect freshness (TC-TIME-01).

## 5. Status Classifications (must remain distinct)
1. VALID — Recent, correctly structured data passing sequence, instance, and content checks.
2. STALE — Time since last newly validated reading exceeds 1,500 ms (client monotonic clock).
3. MISSING — Expected polling interval elapsed with no network response.
4. INVALID — Schema violation, sequence regression, conflicting payload under same instance+sequence, or other validation failure.
5. SERVICE_UNAVAILABLE — State service endpoint unreachable, timeout, or non-2xx.
6. RENDERER_UNAVAILABLE — Application process unresponsive (distinct from internal rendering-loop failure; core prototype may defer full frame-progress signal).

## 6. Diagnostic Record Format
```json
{
  "diagnostic_timestamp": "2026-10-25T22:00:01Z",
  "test_id": "TC-RESTART-01",
  "status_classification": "SERVICE_UNAVAILABLE",
  "observed_condition": "Connection refused on loopback port 8080",
  "expected_outcome": "Client transitions to unavailable state without crash",
  "result": "PASS | FAIL | INCONCLUSIVE | PENDING"
}
```

## 7. Timing Parameters (experimental, require validation)
- Telemetry generation: 500 ms
- Client polling: 250 ms
- Client HTTP timeout: 1,000 ms
- Stale threshold: 1,500 ms (client monotonic clock from last newly validated reading)
- Unavailable threshold: 3,000 ms

## Authorization Boundaries
No privileged host modifications, persistent services, autonomous scheduled routines, or external publication.  
Manual host recovery only.  
A/B/C are conditionally authorized for bounded experiment; they may transition to EXPERIMENT upon freeze of this contract without additional authorization.  
D/E remain specification-only.

---

Clarifications CR-01, CR-02, and CR-03 are incorporated.  
Ready for Specula’s verification. Upon confirmation, Nexus will freeze CFX-M001-CONTRACT-v0.1 and update A/B/C status.  
No code has been written. No experiment has begun.
