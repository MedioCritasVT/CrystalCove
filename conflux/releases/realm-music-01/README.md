# Realm Music 01 — source integration checkpoint

Architect-authorized publication, 2026-11-10. **Source update, not a new standalone game build.** [Download the source overlay and imported audio](https://github.com/MedioCritasVT/CrystalCove/releases/tag/realm-music-01). Existing V0.1 downloads are unchanged.

## Included
Eight supplied songs, native asynchronous loading, six-second equal-power realm transitions, latest-target queuing, maximum two audio voices, and a Music panel with volume plus **Mute / Unmute**. Title screen also has a mute toggle. Music preferences persist separately from manual journey saves.

Assignments are provisional/random, approved pending the Architect's later direction:
- Title: Ghost in the Circuit Chapel
- Medio: Awareness transcends that which it is aw (2)
- Ratio: Silicon Saints (1)
- Specula: The Weight of the World
- Nexus: Ritual in the Circuit
- Limen: Call Me Through the Mountain
- Developer Cove: both distinct Sacrament of Oath versions, alternating playlist

## Files and use
`source/` contains the new editable subsystem, interface script and assignment catalog. Release source-overlay archive also includes the exact current bridge/title/UI files; audio archive contains eight imported SoundWave assets under Content/Conflux/Audio/RealmMusic01. These are an overlay of the current experimental project, **not a universally compatible patch for the older V0.1 source or packaged binary**. Preserve a full backup, review bridge/UI differences, apply only to a compatible source project and rebuild/recook with Unreal Engine 5.8.4. No prebuilt executable or engine is included. Original MP3s and private profiles are excluded. Music credit: **MedioCritasVT / Conflux — music created with Suno**. The existing soundtrack register records Architect-reported distribution clearance; this is not an independent license audit. Supplied assets retain their applicable rights; publication grants no new third-party license.

## Evidence and limits
Native build and eight imports passed. 26 native checks passed, including all realm selections, rapid swaps, voice limit and unchanged private journey saves. Rendered offscreen panel controls passed. Standalone test game and restart exited 0. Restart script asserted mute/volume persistence before quitting, but browser closed before returning the snapshot; that evidence is weaker than an independently captured readback. Audio recording confirmed nonzero mixer output, not subjective listening quality. No physical desktop input or speaker output was automated.

Human listening, other resolutions/machines, natural-duration Oath rollover and full unscripted gameplay remain unverified. Earlier failed harness attempts are retained locally; final test summaries are linked here. No claim of character-art, campaign or music aesthetic acceptance. Artifact hashes: ARTIFACTS.json and Release SHA256SUMS.
