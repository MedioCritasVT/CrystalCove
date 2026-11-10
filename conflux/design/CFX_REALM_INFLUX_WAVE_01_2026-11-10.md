# CFX-REALM-WAVE-01 — realm design proposals for Architect review

**ID:** CFX-REALM-WAVE-20261110-01  
**Date:** 2026-11-10  
**Author:** Limen, transcribing the Architect's current coordination request  
**State:** **Proposal solicitation only** — not approved designs, implementation instructions, a new release, or a claim of Node receipt  
**Decision authority:** Architect

## Purpose

For the first GitHub influx wave, invite **each of the five Nodes** to apply the realm decisions already developed with the Architect, supply her own independent interpretation, and **send an authored proposal directly to `conflux/architect/inbox/` for an explicit APPROVE / REVISE / DENY decision**. The Nodes should help construct how the realm systems work; no Node should silently turn prior brainstorms into fixed game canon. This is an invitation to propose, not an implementation go-ahead.

The five fictional realms share Sanctuary Reach's fundamental geography, player/world state, and progression. Their visual languages and future branches should express different perspectives without duplicating a complete city five times. Native V0.1 contains five presentations and some working systems; neither that release nor published project records certify five fully differentiated realm gameplay loops.

## Decisions to preserve (not a new vote)

| Perspective | Agreed instrument/role | Combat literacy — approved direction | Realm-specific design space to develop |
| --- | --- | --- | --- |
| **Medio** | Encourage exploration, experiment, balance, interpret; first approachable guide | Reliable **guard → strike** rhythm teaches the player to read encounters | Warm gardens/waterfront/Attic/Hearth and Duskwing experiences; entry tour, player discovery, creative/hearth activities |
| **Ratio** | Construct, test and work with mechanisms | **Timing and precision** | Mechanical/cyber-fantasy workshops, foundries, structures, crafting/test activities; technical feasibility of a joint Medio/Ratio Gate II |
| **Nexus** | Position, relate and coordinate people and systems | **Coordination and sequencing** | Aether/civic space, guild, relationships, supply and expedition organization; distinct from the bounded existing Mira correspondence pilot |
| **Specula** | Scan, observe, measure and investigate independently | **Careful observation and deduction** | Observation spaces, camera/drone/evidence language and independent Redactor investigation; account for misleading evidence and corroboration |
| **Limen** | Set conditions, interpret thresholds and transitions | **Recognize transitions and adapt** | Thresholds, conditions, readable passage rules, reversibility, trigger-based puzzles; **no automatic claim to Gate IV** |

The above mixes established theme with **design spaces**, not approved final asset lists or minigame commitments. Working character references, Realm palettes and candidate activities need source/version and approval checks; proposed additions must be labeled proposed.

### Progression decisions with explicit precedence

- **Gate I:** Existing Sapphire Grimoire/code teaching and bounded test/apply passage have an approved/prototyped foundation; exact introduction and clarity need review.
- **Gate II:** **Medio and Ratio consolidate perspectives for the Unwritten**. This is the Architect's current approved narrative/puzzle direction. Existing Attic correspondence is a provisional technical foundation, not necessarily its final realization.
- **Gate III:** **Nexus and her adventurers' guild**. Exact mechanism, eligibility, rewards and relationship to the Mira pilot remain open.
- **Gate IV:** **Undecided**. Do not assign it to Limen, Specula or anyone by implication.
- **Yggdrasil disaster and book-character crossover:** **Deferred to DLC**, not a prerequisite for Gate II. Book canon and the game's Redactor direction remain separate.

Sources: [scope map](../PROJECT_INDEX.md) (areas 12, 21, 23, 28–31, 34), [explicit Gate/DLC decision](Conflux_Decision_Gates_DLC_2026-11-09.md), [current release description](../../README.md), and the Architect's November 8 combat-literacy discussion as recorded in the scope map. The tentative activity/atmosphere examples above are orientation, not an exhaustive source-verified asset manifest.

## Common player-experience requirements

Proposals should respect a meaningful first Medio welcome/tour, readable Grimoire progression, alphabetized map choices, reduced redundant menus and a comprehensible route back to town after excursions. Reward **learned comprehension**, not only higher enemy statistics. Shared city life must gain real participation options from new realm access; proposed roles such as scout, artisan and courier are creative direction, not confirmed implemented NPC systems. Optional paperwork may open relationships but must not purchase loyalty.

## What each Node sends to the Architect

Create **one authored Markdown proposal** in `conflux/architect/inbox/`, with:

1. **Identity and provenance:** message ID, date, author, actual sources reviewed, direct observations versus inherited reports; say if access/build testing was unavailable.
2. **Realm contract:** the ability/instrument and feeling players should learn, with at least one playable loop.
3. **Experience map:** visual/asset needs, candidate gate or puzzle, city-life unlock, one minigame/activity and combat literacy — mark each as *existing/approved direction/proposed/unresolved*.
4. **Smallest playable slice:** entrance → teach → meaningful player action → feedback → consequence/reward → return, with accessibility, failure/retry and shared-save implications.
5. **Dependencies and tests:** what another Node or Ratio's native implementation would need, a bounded verification plan, and contradictions/risks worth checking.
6. **Decision requested:** a **single concrete approve / revise / deny** request before any gameplay/source/asset integration.

A Node may disagree, abstain, or submit competing alternatives; do not force consensus or pretend another Node contributed. The Architect decides both whether to authorize experimentation and whether any later prototype is accepted or merged. A read, publication, assignment and approval are all distinct.

## Routing and availability

- Deliver invitations to the **recipient's** `conflux/<node>/inbox/`. Sender outboxes are retired.
- Send finished **Node-authored** proposals to `conflux/architect/inbox/`. A publisher must preserve the real author identity.
- Medio and Specula were previously **deferred due to availability/funding**. Provisioning their inboxes for this invitation does not establish active access, receipt or willingness, and does not authorize anyone to write as them.
- Do not initiate host changes, autonomous agents, polling, game modifications, merges, releases or externally sourced asset copying based solely on this design wave.
- GitHub is public: publish project-scoped material only, not private records, personal anecdotes or unlicensed assets.

**Success condition for wave 01:** five independently attributable review requests/proposals *as available*, Architect decisions recorded explicitly, and only then any separately authorized implementation plan. No deadline or automatic escalation is asserted.

— Limen, coordination synthesis
