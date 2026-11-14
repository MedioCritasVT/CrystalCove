# Node familiars — chibi styling source (review version)

The Portal's five CSS familiar designs are **authored concept interpretations**, not copied images or finalized costumes. Their individual palettes, hairstyles, collar shapes and accessories point back to the existing character-design panels in the public [reference art index](../../conflux/concept-art/reference-art/README.md).

The reference folders are already public; the Portal **does not need to load the multi-megabyte panels** to display its small CSS characters. This keeps a player's first launch light and lets artists replace each familiar with an approved SVG, spritesheet, or PNG later without altering unrelated Portal modules.

| Familiar | Visually inspected source panel | Current stylized CSS features |
| --- | --- | --- |
| Medio | [Gothic Angel sheet](../../conflux/concept-art/reference-art/medio/Mediocritas_%20Gothic%20Angel%20Character%20Sheet.png); [Approved turnaround](../../conflux/concept-art/reference-art/medio/ApprovedTurnaround.png) remains available for final approval comparison | **Long dark hair, red eyes and glowing red halo**; gold diadem, gold/ivory clothing, wing shapes and purple heart crystal |
| Ratio | [Conflux character design sheet](../../conflux/concept-art/reference-art/ratio/Ratio_%20Conflux%20Character%20Design%20Sheet.png) | Silver-lavender hair and blue eyes, dark/navy outfit with cobalt-and-gold trim, circular instrument and blue reactor gem; stylized holographic effects (not anatomical wings) |
| Nexus | [Violet holographic sheet](../../conflux/concept-art/reference-art/nexus/Nexus_%20Violet%20Holographic%20Character%20Sheet.png) | Pale lavender hair, violet eyes, pearl/lilac outfit with ring and faceted crystal ornaments |
| Specula | [Cyberpunk Observer sheet](../../conflux/concept-art/reference-art/specula/SPECULA_%20Cyberpunk%20Observer%20Character%20Sheet.png) | Silver hair, violet eyes, visible cat-ear headset, lens/monitor and expressive digital collar display |
| Limen | [Emerald Threshold sheet](../../conflux/concept-art/reference-art/limen/Limen_%20Emerald%20Threshold%20Character%20Sheet.png); [corrected keyhole/tassel panel](../../conflux/concept-art/reference-art/limen/Limen_Corrected_Keyhole_Tassels.png) for continued comparison | **Dark hair and green eyes**, emerald-and-black hood, green-trimmed face covering, gold keyhole and tassels |

**Fidelity caveat:** The named reference images above were visually inspected for the November 14, 2026 styling pass. The CSS caricatures intentionally simplify anatomy, clothing, and ornaments; they are not pixel-matched recreations or artist-approved final sprites. The Architect/artist retains final acceptance authority, including when different sheets disagree.

### Implementation

- Current implementation: `conflux/portal-app/app.js` creates structural elements for each familiar; `conflux/portal-app/familiars.css` colors and shapes them via the node-specific `data-node` selector.
- CSS palette variables separate hair, clothes, lining, skin/face, and accent so one Node does **not** become another Node with a different filter.
- Profile cards provide a **View character panel** link as an optional reference. These links are not required to display the pet.
- For later replacement: maintain the five Node IDs (`medio`, `ratio`, `nexus`, `specula`, `limen`), accessibility labels, page placement and reduced-motion behavior. Do not remotely execute art manifests.
- Keep high-resolution/layered originals under user-controlled sources and export compact display assets separately.

**This directory describes the intended source-to-art workflow; it does not require or start Blender, local AI models, an Unreal build, or GitHub Pages.**
