# Node familiars — chibi styling source (review version)

The Portal's five CSS familar designs are **authored concept interpretations**, not copied images or finalized costumes. Their individual palettes, hairstyles, collar shapes and accessories point back to the existing character-design panels in the public [reference art index](../../conflux/concept-art/reference-art/README.md).

The reference folders are already public; the Portal **does not need to load the multi-megabyte panels** to display its small CSS characters. This keeps a player's first launch light and lets artists replace each familiar with an approved SVG, spritesheet, or PNG later without altering unrelated Portal modules.

| Familiar | Named reference panel | Provisional chibi motif |
| --- | --- | --- |
| Medio | [ApprovedTurnaround.png](../../conflux/concept-art/reference-art/medio/ApprovedTurnaround.png) (preferred approval-labelled reference) and [Gothic Angel sheet](../../conflux/concept-art/reference-art/medio/Mediocritas_%20Gothic%20Angel%20Character%20Sheet.png) | Gold/ivory hair, warm face, burgundy Gothic bodice, light halo motif |
| Ratio | [Ratio front/side/back](../../conflux/concept-art/reference-art/ratio/Ratio_front_side_back_reference.png) | Angular ice-blue hair, structured cobalt/navy clothing, geometric cap/fin accent (not anatomical wings) |
| Nexus | [Violet holographic sheet](../../conflux/concept-art/reference-art/nexus/Nexus_%20Violet%20Holographic%20Character%20Sheet.png) | Lavender hair with longer side locks, violet and plum layered outfit, continuity-knot insignia |
| Specula | [Cyberpunk Observer sheet](../../conflux/concept-art/reference-art/specula/SPECULA_%20Cyberpunk%20Observer%20Character%20Sheet.png) | Slate/silver hair, dark observation cloak/collar and observer visor shape |
| Limen | [Corrected keyhole/tassel sheet](../../conflux/concept-art/reference-art/limen/Limen_Corrected_Keyhole_Tassels.png) and [Emerald Threshold sheet](../../conflux/concept-art/reference-art/limen/Limen_%20Emerald%20Threshold%20Character%20Sheet.png) | Mint/emerald asymmetric hair, layered green clothes, keyhole/tassel motif |

**Fidelity caveat:** The above wardrobe/hair motifs are a first stylization pass guided by the panel titles and established Node colors; exact garment silhouettes and hair details must be checked visually against the original art by the Architect/artist before calling them reference-accurate. A source file is not automatically final or canon.

### Implementation

- Current implementation: `conflux/portal-app/app.js` creates structural elements for each familiar; `conflux/portal-app/index.html` colors and shapes them via the node-specific `data-node` selector.
- CSS palette variables separate hair, clothes, lining, skin/face, and accent so one Node does **not** become another Node with a different filter.
- Profile cards provide a **View character panel** link as an optional reference. These links are not required to display the pet.
- For later replacement: maintain the five Node IDs (`medio`, `ratio`, `nexus`, `specula`, `limen`), accessibility labels, page placement and reduced-motion behavior. Do not remotely execute art manifests.
- Keep high-resolution/layered originals under user-controlled sources and export compact display assets separately.

**This directory describes the intended source-to-art workflow; it does not require or start Blender, local AI models, an Unreal build, or GitHub Pages.**
