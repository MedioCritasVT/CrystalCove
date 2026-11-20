# Conflux Soundtrack — album and public MP3 register

**Original album checkpoint (2026-11-14):** **Eleven supplied MP3 recordings across ten distinct compositions** have been verified by exact SHA-256 checksum. Seven match the [original manifest](RELEASE_SHA256SUMS.txt) byte-for-byte; the four further recordings (three from the first Architect EP and *Silicon Saints*) now appear in the [complete eleven-recording manifest](RELEASE_SHA256SUMS_FULL.txt). Both *Sacrament of Oath* takes remain independent versions.

**Expanded publication (2026-11-19):** the [official GitHub Release](https://github.com/MedioCritasVT/CrystalCove/releases/tag/conflux-soundtrack-v0.1) retains the original [11-recording ZIP](https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-soundtrack-v0.1/Conflux_Soundtrack_11_Recordings_Release_Ready.zip) and now includes **17 additional individual MP3 assets** across sixteen further compositions, including both filename variants of *From the Smallest Corner*. Total catalog: **28 recordings across 26 compositions**. Release filenames and byte sizes were verified from GitHub; the newly uploaded actual audio bytes, full SHA-256 and durations have **not** been independently checked. The eleven original recordings remain SHA-verified inside the ZIP but are not yet uploaded as individual MP3s.

| Composition | Recording(s) | Approx. duration | Source status |
| --- | --- | ---: | --- |
| Awareness transcends that which it is aw… | 1 | 3:35 | SHA-verified, title was truncated in source |
| Call Me Through the Mountain | 1 | 4:03 | SHA-verified |
| Ghost in the Circuit Chapel | 1 | 3:56 | SHA-verified |
| Ritual in the Circuit | 1 | 3:24 | SHA-verified |
| The Weight of the World | 1 | 3:00 | SHA-verified |
| **Sacrament of Oath** | **Take 1 + Take 2** | **2:25 + 2:26** | Both SHA-verified distinctly |
| Who Gave You the Crown? | 1 | 4:24 | SHA-verified |
| Little Adventurer | 1 | 5:26 | SHA-verified |
| LITTLE GODS IN WHITE GLOVES | 1 | 5:43 | SHA-verified |
| **Silicon Saints** | 1 | 2:49 | SHA-verified, added to public catalog |

[Machine-readable catalog](catalog.json) contains exact release filenames, sizes and provenance. Full SHA-256 hashes and durations apply only to the original eleven album recordings.

## New standalone MP3 assets — November 19, 2026

These 17 files were publicly uploaded by the Architect. Exact filenames and byte sizes were retrieved from the official GitHub Release API, but the audio itself was not independently hashed or listened to. The two *From the Smallest Corner* filename variants are retained separately. The filename `Wake.the.Kindness.in.the.mp3` is truncated; its displayed title remains provisional.

| Display title | Assets | Collection | Exact filename(s) |
| --- | ---: | --- | --- |
| A Bowl with Room | 1 | Additional | `A.Bowl.with.Room.mp3` |
| Alchemia | 1 | Node suite | `Alchemia.mp3` |
| BEFORE WE SAY YES | 1 | Additional | `BEFORE.WE.SAY.YES.mp3` |
| Emotion, a Voice in the Weave | 1 | Additional | `Emotion.a.Voice.in.the.Weave.mp3` |
| From the Smallest Corner | 2 | Additional | `From.the.Smallest.Corner.1.mp3`, `From.the.Smallest.Corner.mp3` |
| Hospes Hosting | 1 | Node suite | `Hospes.Hosting.mp3` |
| Leave Room Around It | 1 | Additional | `Leave.Room.Around.It.mp3` |
| Limen Protocol | 1 | Node suite | `Limen.Protocol.mp3` |
| Medio Design | 1 | Node suite | `Medio.Design.mp3` |
| Nexus Continuity | 1 | Node suite | `Nexus.Continuity.mp3` |
| NO CROWN ONLY KEYS | 1 | Additional | `NO.CROWN.ONLY.KEYS.mp3` |
| ONE LITTLE STEP | 1 | Additional | `ONE.LITTLE.STEP.mp3` |
| Ratio Verification | 1 | Node suite | `Ratio.Verification.mp3` |
| Specula Audit | 1 | Node suite | `Specula.Audit.mp3` |
| THE MIDDLE ISN'T EMPTY | 1 | Additional | `THE.MIDDLE.ISN.T.EMPTY.mp3` |
| Wake the Kindness in the… | 1 | Additional | `Wake.the.Kindness.in.the.mp3` |

## Original verified album and individual-track releases

The complete archive `Conflux_Soundtrack_11_Recordings_Release_Ready.zip` (57,270,992 bytes) is publicly downloadable from the official GitHub Release. This asset lives outside the Git tree and is available without a Git account, Git clone, or Portal. The local Portal optionally installs it via **Music options → Install all 11 tracks from GitHub**, verifying the source and per-recording hashes. Existing source files and local private originals remain separate.

The Portal cannot stream separate tracks directly *out of a remote ZIP*, but can discover and stream the newly attached standalone MP3 assets on user selection. Direct streaming for the eleven original recordings still requires separately uploading those originals under their catalog filenames. The 7- and 11-track ZIP installer remains restricted to the existing checksum-verified originals, not the newer individual MP3s.

If the local ZIP has become unreadable, restore or copy a readable ZIP into Downloads before uploading. Do not upload just the `SHA256SUMS` manifest, a folder shortcut, or a ZIP whose files failed verification. Owners should review any third-party generation/service distribution terms before publishing.

## Releases versus sources

- **Editable/original music and artwork sources** belong in a user-controlled working-source collection; see [Sources](../../sources/README.md). A Git clone should not inherit tens of megabytes of raw audio or proprietary session files by default.
- **Catalog and SHA manifests** are versioned here on GitHub. They are public metadata, not recordings.
- **Distribution:** the seventeen newer standalone MP3s are already attached to the public release; the eleven original recordings remain downloadable via the verified ZIP, not as individual public MP3s. Attach them separately under their catalog names only if direct original-track streaming is desired.
- The Portal's **Music options → Install soundtrack ZIP once** accepts a complete, verified **7-track legacy** or **11-track full** archive. Neither ZIP installer makes a GitHub upload.

The verified original album ZIP remains separate from the Git checkout. The 17 new standalone MP3s are publicly listed; 11 original standalone files remain unpublished.

## Attribution and publication boundaries

The Architect supplied these recordings and requested inclusion. Some ID3 metadata identifies Suno-assisted creation and the `mediocritasvt` creator account. For the original seven the Architect previously confirmed distribution eligibility; the later recordings' public distribution request is on record. **This is a user attribution/approval statement, not an independent rights audit.** Before publishing, the Architect should verify terms applying to every recording, release credits, and intended licensing.

Suggested credit: **MedioCritasVT / Conflux — music created with Suno** (subject to Architect review). Public listening/download does not automatically grant permission for unrelated remixing, synchronization, sublicensing or commercial use; no Creative Commons license is declared by this catalog.

## Future changes

The Portal discovers official GitHub Release assets through the Release API. It neither creates release assets nor auto-plays music; matching filenames and sizes do not establish audio content hashes. Genre categorization, album sequencing, normalization, placement in Unreal, opening/closing-theme choices and canonical versions remain design and test work.

**Architect authority:** The Architect chooses what is distributed, included in the native game or accepted as final.
