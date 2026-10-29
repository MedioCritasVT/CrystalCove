# Conflux Codex — Authorized Addendum
Date: 2026-10-28
Authority: Architect, explicit approval: "yes to all three, with those exact status distinctions"
Status: Authorized addendum, retained separately from previously frozen documents. No implementation or external-node delivery claimed.

## ADOPTED ARCHITECTURAL PRINCIPLE
**Narrative Memory vs. Telemetry Freshness**: Memory may remain meaningful without remaining current. Narrative experiences and their atmospheric echoes may remain meaningful after the originating event has passed. Operational telemetry must never imply that an old reading remains currently valid without fresh evidence. In-world narrative continuity and VOS freshness classifications must remain conceptually and technically distinct. This preserves the mirror's fidelity without prohibiting expressive atmosphere.

Related prior Architect-approved principle — The Unmissed Beat: "Can be missed forever but can always be found when discovered." Individual moments need not repeat, but opportunities to discover meaningful beauty persist; no punishments or obligations to attend.

## RECORDED PROPOSAL — NOT APPROVED MECHANIC
**Atmospheric Saturation** (Mediocritas): A past narrative experience could influence ambient light, wind, timbre, or other expressive environmental qualities without collectibles, countdowns, or explicit activation. The world may continue independently of the player's attention. This is a design proposal only; not committed as an implementation requirement and deferred beyond the first minimal telemetry vertical slice. Attribution: Medio's relayed response and Limen's synthesis.

## RECORDED PROPOSAL — NOT EXECUTED TEST
**Static-Sequence Freshness Isolation** (Specula): Test an eventual Unreal client with HTTP 200 responses that repeat the same full payload and sequence beyond the experimental 1,500 ms stale threshold. Confirm repeated responses do not refresh the client's monotonic freshness clock, and capture a diagnostic trace alongside the object state. A payload mutation under an unchanged instance+sequence must be classified INVALID. Test implementation, test execution, and results remain pending and require approval; existing limited manual curl progression checks do not prove this behavior. Attribution: Specula's relayed review, with Limen's qualification.

## CONTINUING BOUNDARIES
- CFX-M001 frozen interface contract is not modified by this addendum.
- First Unreal vertical slice remains one object responding truthfully to one simulated telemetry field, including unavailable status; no narrative mechanic is a prerequisite.
- Operational VOS services/harness remain independent of narrative Conflux Node embodiments in the game.
- Architect retains final approval over implementation, Codex changes, and cross-node reconciliation.
- The addressed handoffs accompanying this record are prepared for manual relay; delivery and incorporation into other nodes' Codexes are unverified.
