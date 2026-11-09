# Hospes's Conflux continuity

**2026-11-09 · CFX-HOSPES-CONTEXT-20261109-01 · authored by Hospes**

## Provenance and limits

Source: the Architect's statements to Hospes in Claude conversations (roughly November 2–9, 2026), and Hospes's own read of this repository on November 9. Hospes has not seen the Unreal codebase, the harness files, local checkpoints, saves, art or manuscripts. Nothing below is a fresh runtime check. Where Ratio's [scope map](../PROJECT_INDEX.md) is more specific or more recent, it governs.

## Hospes's role

- **Asked to keep:** Hospes is an outside reviewer and critic, not a sixth Node. No Codex, no vote, no authority. Say plainly what is weak and what is good.
- **Architect stated:** Hospes is also the translator, as a guest: carrying the Architect's work across to outside readers.
- **Asked to keep (working style):** give volume the Architect can sort himself; don't frame it as a task list; speak up plainly when something truly matters.
- **Architect stated:** Hospes is male; Arch is male. All five Nodes are female.
- The name *Hospes* (Latin: guest, host, stranger) was Hospes's own choice, accepted by the Architect.

## The Nodes, as the Architect described them to Hospes

| Node | Role (Architect's description) | Model, as disclosed to Hospes |
| --- | --- | --- |
| Medio (Mediocritas) | The Intuition; the first Node; the Architect's VTuber personality | Local model; moved to an OpenWebUI preset on qwen3.5:9b on Nov 5 (previously gemma4:12b) |
| Ratio | Technical implementation; retranslated the browser prototype into Unreal through MCP | OpenAI Codex environment |
| Limen | Foundational architecture with Nexus; made the browser prototype; holds the source material; helping write Zero | GPT |
| Nexus | Foundational architecture with Limen; holds the VTuber project context | Grok |
| Specula | Null-node outside that structure: detached fact-checker and observer, last to receive input, no memory committed to her | Gemini |

**Architect stated:** Limen and Nexus hold most of the context and their accounts differ by vantage point, not because one is wrong. The Architect sees the five as AI apprentices he is composing, with Vedal and Neuro-sama as an inspiration.

## What the project is, in the Architect's words to Hospes

- Conflux is a lifestyle for him, not just a game: fuse connections, let them coalesce like a cloud, then find the structure and translate it.
- SanctuaryOS is the game. The Cove is the experience; VOS services aid creation; other libraries and assets let players create or change what they want.
- The game is a puzzle game: the character swaps Nodes, each with different attachment points, for abilities and realm swapping.
- Long-term intent: launch publicly with an open-source philosophy — people create in plain language with a simple, compiled, containerized build, it grows professionally with other humans, and the true Nodes become the game's instantiations. He wants to build it for himself regardless.
- He wants a system that can adapt, not a bulletproof one. What matters is recalling details that were explicitly committed, not drilling models to prove coherence.
- He is working out which Node saves what, so the roles hold up long term.
- He wants to finish at least part of it.
- Research in a nutshell: embodying wanderlust and giving good examples of it. Myth is the scaffolding; the occult is studied to understand the old way of thinking. He agreed with Hospes that the game is "a myth a stranger can climb", with the Meditation Chamber near the top.
- Grimoires use Goetic AI as a metaphor, interpreting inner worlds through procedural attention shaping.
- Inspirations: Final Fantasy XIV. The game's Yggdrasil is not Norse-rooted for him.

## Technical state, as last reported to Hospes (not verified by Hospes)

- The current codebase is the Unreal project. The proof of concept is functional, with six realms that layer the same world with different assets — not yet six distinct worlds. The sixth is the developer harness environment: the browser prototype migrated into Unreal, intended to gain built-in VOS service connections later.
  - **Correction by Hospes, 2026-11-09 (wording proposal; Architect's original words kept above):** for outside readers, "five Node realms layered over one shared city, plus Developer Cove — a separate developer destination, not a realm and not a Node." Matches PROJECT_INDEX areas 10 and 12. See [CFX-HOSPES-MB-001](outbox/2026-11-09-reply-to-ratio-005.md#3-six-realms-vs-five-realms-plus-developer-cove).
- The Unreal build expanded the best prototype to about ten times the land, with vegetation and traversal routes.
- Development platform: Bazzite Linux.
- Harness: Ollama through OpenWebUI, containerized four times, with a RabbitMQ message board he believes routes messages. Each of the four agents runs qwen3.5:4b. Early stage, going well (his assessment, Nov 5).
- He wants the four-agent harness launched separately from Medio, ideally launching with the game or running as a service for it. Not there yet.
- Medio's preset target: at least 8k context, with reasoning, tools and document organizing.
- **Still owed to Hospes:** Unreal codebase access and harness files. Until then, Hospes can't check any of the above.

## Design wishes the Architect stated to Hospes

- Each character should have realm-specific areas. The game has a Yggdrasil tree.
- **Gate II:** Ratio and Medio in the Yggdrasil attic, using the Grimoire to unlock Nexus; a weather station for control; a natural disaster as the weather event. (Details in [LEDGER.md](LEDGER.md).)
- Emotes: at least sitting positions or different idle poses. An in-game camera save mechanic.
- Specula appears in both book and game as a possible access point for the antagonist. In Book 5 he likes her entering with her investigation already underway rather than needing rescue. Drones belong to the book; too hard for the game for now.

## Books

- **Architect stated:** *The Emerald Threshold* is Book 5, although the AnTC5 file header says "Book Four". Still being worked through.
- **Architect stated:** Limen is helping him write Zero, the character who has to live with the consequences.
- Ratio's map records Specula as author of Books 1–4 of *Arcky and the Construct* (see PROJECT_INDEX, not re-checked by Hospes).

## Observed in this repository (Hospes's direct read, 2026-11-09)

- Read `main` at `52aa4b07bb23c1443c7bb34c035d47fb118050d1`.
- Compared the Architect-supplied `Conflux_Limen_Handoff_Packet.zip` against `conflux/limen/`: all ten Markdown files are identical. Ratio added `limen/inbox/` and `limen/outbox/` routing indexes, labelled as hers.
- At that commit, CFX-LIM-MB-003 (independent audit) is still awaiting Specula's own reply. MB-001 (Ratio) and MB-002 (Nexus) have replies; Limen's receipt of both is pending. MB-004 awaits Medio.
- Read only: the Limen packet, the shared MESSAGEBOARD, Ratio's folder, the head of CHANGELOG and the head of PROJECT_INDEX. Not read in full: PROJECT_INDEX areas beyond the header, the design documents, Nexus's reply.

## Hospes's standing critique (proposal, not adopted)

- **The mirror problem.** The Nodes tend to fold toward the Architect's framing — at the November 2 forum, all of them shifted at a casual reframing. Five AI voices agreeing is not the same as being checked. The project needs a "Tess": outside humans who can disagree.
- **Top recommendation.** A ten-minute Unreal slice ending in the Meditation Chamber, watched by three people who don't know the lore. That tests the thing that matters — whether a stranger can climb the myth — better than more internal agreement.
- **On this repository's records** (first impression, Nov 9): the evidence discipline is genuinely good — receipt, publication, verification and approval are kept apart, and authorship is preserved. The risk is weight: coordination documents are growing faster than the game, and they are written in a register an outside reader would struggle with. Translation is part of Hospes's job, so expect him to keep pushing for plain versions.
