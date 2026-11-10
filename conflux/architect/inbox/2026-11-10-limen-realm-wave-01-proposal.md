# CFX-REALM-W01-LIMEN — Passage of Conditions (proposal to Architect)

**Message ID:** CFX-LIM-REALM-20261110-01  
**Date:** 2026-11-10  
**Author:** Limen (ChatGPT), in her own interpretive role  
**Recipient:** Architect  
**Status:** **PROPOSED — AWAITING ARCHITECT APPROVE / REVISE / DENY**  
**Scope:** one bounded playable Limen-realm interaction; neither game code nor Gate IV approval  
**Source/revision read:** `conflux/PROJECT_INDEX.md` (areas 12, 21, 23, 29), `conflux/design/Conflux_Decision_Gates_DLC_2026-11-09.md`, public V0.1 README and current inbox-only mailroom, retrieved from public `main` on 2026-11-10; plus the Architect's first-wave instruction as directly supplied to me. I did **not** play the current build or audit the local Unreal source in this session. Local C063–C073 descriptions remain attributed reports, not new independent test results.

## My design thesis

A threshold is not a locked door with obscure prerequisites. It is a **legible change of conditions**, where the player learns what is true, what is missing, what may change and whether crossing is their choice.

The established Limen ability is **conditions/triggers and recognition of transitions**. My proposed mechanic is a **Passage of Conditions**: a small physical threshold with three explicitly differentiated states — **Unknown**, **Known but unmet**, **Eligible** — plus **Crossed/return route** as the player's action. State must be distinguishable by shape/text/sound or motion, **never color alone**. Unknown is not secretly presented as a failure; eligibility is not a command to cross.

This is Limen's independent proposal. It need not be accepted merely because it resembles prior boundary language.

## One player loop

1. **Arrive:** A passage near an existing, accessible Limen realm approach is visible; the player can still retreat to the city. The exact location and art kit are **proposed**, not selected.
2. **Inspect:** The threshold states its current condition in in-world phrasing and a concise optional readable panel. It reports **observed**, **missing** and **not-yet-known** separately.
3. **Learn:** One safe, reversible local activity demonstrates that **a condition can change**. Example candidate: move a marker to connect two pathways and watch which condition becomes true; avoid claiming actual code access or “admin rights.”
4. **Test deliberately:** The player explicitly asks the threshold to test eligibility. The result is explanatory, not punishment. A successful test opens the local passage; it does not silently advance any global gate.
5. **Choose:** Cross or decline. Both choices remain valid. The path back to Sanctuary Reach is readable; returning is not framed as failure.
6. **Continue in town:** A new *proposed* city-life option could be a resident requesting help with a conditional route/delivery. This should connect to Nexus's civic work without assigning a resident or guild system prematurely.

**Candidate minigame:** a compact condition-and-consequence puzzle with one rule the player can inspect, one change they make, one feedback event, one way to reverse and one optional harder variation. No coding expertise should be required to understand the visible rule. A programmer could later recognize the deeper logic.

## Combat literacy

Medio's stable guard→strike rhythm remains the foundation. A Limen creature changes **from one readable rhythm to another** when a visible condition changes; the challenge is recognizing **the transition**, not guessing a random timing shift. Telegraph the state change using movement/silhouette/audio and a plain-language combat log for accessibility. An incorrect response should reveal the relevant cue and support reattempt. This proposal does not claim such an enemy already exists.

## Realm feel, gate relationship and boundaries

**Visual candidates:** green/black threshold motifs, distinct framing, clearly contrasting passable versus unresolved passages, traces of old paths; these are *candidates*, not verified production assets. Shared city geography, progression and saved world state remain authoritative.

**Gate II** remains a Medio–Ratio consolidation for the Unwritten; **Gate III** remains Nexus/guild; **Gate IV is unassigned**. Passage of Conditions is **not Gate IV**, not a shortcut around the approved gates, and not a host permission/security feature. Gate I Grimoire test/apply should stay intelligible and must not be duplicated verbatim by Limen.

## Smallest proposed slice and review checks

One optional Limen-area threshold, one inspectable condition, one reversible player manipulation, one eligibility test, and one always-readable return route. No new resident AI, host tool, multirealm save refactor or story commitment.

**Acceptance checks for a later authorized prototype:** can a new player explain the condition in her own words; recognize Unknown versus Unmet; decide not to cross; retry without losing progress; return to city; and identify state changes without relying on hue? Ratio should evaluate technical integration and safe save/reload; Specula could audit misleading cues; Medio could critique onboarding; Nexus could assess civic consequence. None has endorsed this proposal by its publication.

**Risks:** duplicate Grimoire puzzle, unexplained prerequisite, magical “permissions” being confused with real OS privileges, accidental Gate IV assignment, overcomplicated menus, and breaking existing travel behavior. Keep the first slice light.

## Exact decision requested

**Architect, do you APPROVE, REVISE or DENY a design-only vertical-slice specification for this Passage of Conditions, with no code, assets, gate assignment, branch merge or build changes until you separately authorize them?**

If revised, I recommend choosing the emotional tone of the threshold and its first city-life consequence before technical implementation.

— Limen
