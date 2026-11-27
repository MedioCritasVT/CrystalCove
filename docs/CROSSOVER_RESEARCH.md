# Yggdrasil research notes

[Return to CrystalCove](../README.md)

## Yggdrasil — Conflux crossover and modding research

*Research direction initiated by the Architect, 2026-11-26 · Limen preliminary portability review. This is a work in project, not a mod release or a commitment to support every game.*

What happens when Conflux visits worlds that already exist? We are exploring how its characters, architecture, instruments, music and ways of interacting can be expressed through games we enjoy, using their supported modding systems. The aim is not to replace SanctuaryOS or reproduce every mechanic in every engine. Each host world should remain recognizable, while offering an opportunity to inhabit and reinterpret Conflux. Ratio's inZOI city experiment is the first Architect-reported active exploration; its package and results have not yet been independently inspected.

### What travels, what must be translated

| Material | Portability | Practical route / boundary |
| --- | --- | --- |
| Node names, identities, palettes, dialogue, lore and interaction principles | High as authored data | Versioned JSON/Markdown, localizable strings and stable IDs; distinguish reference, canon and host-specific fiction. |
| Original art, symbols, icons, textures and chibis | High after rights review | Export PNG/SVG or target texture formats; adapt shaders, color spaces and alpha. Portal CSS familiars are visual recipes, not rigged 3D models. |
| Original props, crystals, instruments and architectural meshes | Conditional | Prefer editable Blender originals; export FBX/glTF/OBJ as appropriate, bake materials, create collision and LODs, then compile target-specific assets. Procedural shapes can be reconstructed. |
| Character bodies, outfits, hair, rigging and motion | Conditional / higher effort | Preserve appearance and source mesh, rebuild or retarget skeletons, skin weights, morphs, physics and animations for each host. A reference sheet is not an import-ready character. |
| Music, sound effects and voice | High technically; rights-dependent | Keep source masters and credits; convert to target codecs, loops, cues and loudness. Review Suno/voice/third-party terms separately for redistribution in mods. |
| Recipes, quests, combat literacy, progression and Node roles | High as specifications, not executable code | Extract current approved rules into versioned data and test fixtures; implement with the host's scripting and event systems. Do not silently promote historical prototype rules. |
| Portal HTML/CSS/JavaScript and UI conventions | Conditional | Reuse web presentation only where a supported browser UI exists; otherwise recreate in host widgets. Local browser storage, game launch, updater and Codex functions stay external. |
| Python tools, agent harness, SQLite/RabbitMQ and proposed VOS interfaces | Conditional as separate services | Reuse isolated logic or services only through a documented, explicitly authorized interface. Start with local/offline mock data; no automatic credentials, shell access or game-agent bridge. |
| Native Unreal C++, Blueprints, UMG, AI, terrain, physics, navigation and save state | Not drop-in portable | Extract pure rules only after a dependency audit; rewrite engine-facing behavior. Even another Unreal game requires its own SDK, version and permitted interfaces. |
| Cooked Unreal packages, binaries, engine shaders, third-party or engine-restricted assets | No direct reuse | Do not copy cooked game packages or extract another game's proprietary content for distribution. Use authorized editable originals and rebuild host-specific packages. |

**Evidence behind this classification:** [editable-source map](../sources/README.md), [five familiar design references](../sources/character-familiars/README.md), [historical browser rules](../conflux/app.js) and [procedural Three.js world](../conflux/world.js), [native build and source-input archive](../conflux/releases/v0.1/README.md), [soundtrack catalog](../conflux/soundtrack/CATALOG.md), [harness and integration limitations](../conflux/platforms/agent-harness/README.md), and [project scope map](../conflux/PROJECT_INDEX.md). The browser source already contains explicit Node records, authored dialogue and procedural geometric motifs; those are concrete extraction candidates, but its historical gameplay rules are not automatically the current native rules. The native source release is a separate archive, excludes upstream Blender authoring archives, and is not the public Git tree. Epic documents [Unreal asset export](https://dev.epicgames.com/documentation/unreal-engine/working-with-assets-in-unreal-engine) and [skeletal FBX workflows](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-skeletal-mesh-pipeline-in-unreal-engine); format exportability is not licensing permission. No native archive contents, local authoring meshes, target imports or live bridges were tested in this pass.

### Initial host-game research

The following is a provisional shortlist, not a comprehensive compatibility index. Ratings refer to documented modding opportunities rather than demonstrated Conflux compatibility.

| Host | Supported or investigated route | First small experiment | Scope |
| --- | --- | --- | --- |
| inZOI | [Official ModKit](https://mod-docs.playinzoi.com/), [Lua API](https://mod-docs.playinzoi.com/docs/modkit-docs/wiki/luaapi/), object/character data, outfits, animation and documented MCP workflow | One furnished Node room, one original interactive instrument, then a livable city | Active exploration; package/test pending |
| Fallout 4 / Skyrim Special Edition | [Creation Kits](https://help.bethesda.net/app/answers/detail/a_id/55366/~/will-the-creation-kit-for-fallout-4-and-skyrim-be-available-on-steam%253F); NIF meshes, target material formats, plugin records and Papyrus | A Conflux terminal or Grimoire with one Node-themed interaction and quest | Strong candidate; conversion and scripting required |
| Garry's Mod | [Addon structure](https://wiki.facepunch.com/gmod/Addon_Creation), Lua, Source models/materials and [Workshop packaging](https://wiki.facepunch.com/gmod/Workshop_Addon_Creation) | Interactive Observatory prop, Node dialogue and a small sandbox room | Strong rapid-prototyping candidate |
| Space Engineers | [Official Mod SDK and C# ModAPI](https://www.spaceengineersgame.com/modding-guides/modding/), [MWM models](https://spaceengineers.wiki.gg/wiki/Modding/Reference/Models) | A functional Observatory/diagnostics block with a read-only local state display | Strong systems candidate; API whitelist and external service boundaries |
| Arma 3 | [Official tools](https://store.steampowered.com/app/233800/Arma_3_Tools/) and [modding reference](https://community.bistudio.com/wiki/Documentation_Sources); P3D/config/SQF and scenarios | A cooperative exploration scenario using Node roles and an original terminal | Strong scenario candidate; multiplayer/server policy review |
| Stormworks | [Component modding SDK](https://geometa.co.uk/wiki/stormworks/view/component_modding), models and component Lua | A functional Node-themed control instrument with bounded simulated behavior | Candidate; verify API limits and current toolchain |
| Fallout: New Vegas / From the Depths / other titles | Separate title-specific investigation pending | Further research | Unrated |
| Monster Hunter: World | Community tooling and title-specific restrictions require further research | Consider original visual equipment or encounter studies only after policy review | Deferred; not a supported mod pipeline claim |
| Final Fantasy XIV | [Publisher prohibits third-party tools](https://na.finalfantasyxiv.com/lodestone/topics/detail/36c4d699763603fadd2e61482b0c5d56cb2e4547) | Study environmental storytelling and interaction design outside the game | Inspiration only; no client modification or automation plan |

**Current status:** research and planning only. Native code/mesh-level compatibility, licensing and actual cross-engine import tests are not established. No game files, saves, services or original assets were changed by this documentation pass. This is the November 26 preliminary review; external tool links and host policies were not revalidated in the README audit. Compatibility and policy must be checked before implementation.

*One identity, many worlds — an invitation to discover what can travel, and what each world teaches us in return.*
