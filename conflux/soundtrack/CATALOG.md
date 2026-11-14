# Conflux Soundtrack — verified working release catalog

**Status (2026-11-14):** **Eleven supplied MP3 recordings across ten distinct compositions** have been verified by exact SHA-256 checksum. Seven match the [original manifest](RELEASE_SHA256SUMS.txt) byte-for-byte; the four further recordings (three from the first Architect EP and *Silicon Saints*) now appear in the [complete eleven-recording manifest](RELEASE_SHA256SUMS_FULL.txt). Both *Sacrament of Oath* takes remain independent versions.

**Public album is live:** [Download all 11 recordings in one ZIP](https://github.com/MedioCritasVT/CrystalCove/releases/download/conflux-soundtrack-v0.1/Conflux_Soundtrack_11_Recordings_Release_Ready.zip). The complete asset was verified present in the official [GitHub Release](https://github.com/MedioCritasVT/CrystalCove/releases/tag/conflux-soundtrack-v0.1) on November 14, 2026. **Individual MP3s remain unpublished**, so streaming individual tracks remotely still requires those separate uploads. The Portal can now directly install the verified public album on explicit click, without a local ZIP picker.

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

[Machine-readable catalog](catalog.json) gives stable ASCII release filenames, exact full hashes, durations, and version labels.

## Published complete soundtrack and optional individual-track release

The complete archive `Conflux_Soundtrack_11_Recordings_Release_Ready.zip` (57,270,992 bytes) is publicly downloadable from the official GitHub Release. This asset lives outside the Git tree and is available without a Git account, Git clone, or Portal. The local Portal optionally installs it via **Music options → Install all 11 tracks from GitHub**, verifying the source and per-recording hashes. Existing source files and local private originals remain separate.

An album ZIP upload is **sufficient for public album downloading**, but the current Portal player cannot stream MP3s directly out of a remote ZIP. For browser playback, also attach the **eleven individual MP3 files** under their expected release asset filenames. This can be a later, separate upload; album downloads do not need to wait for it.

If the local ZIP has become unreadable, restore or copy a readable ZIP into Downloads before uploading. Do not upload just the `SHA256SUMS` manifest, a folder shortcut, or a ZIP whose files failed verification. Owners should review any third-party generation/service distribution terms before publishing.

## Releases versus sources

- **Editable/original music and artwork sources** belong in a user-controlled working-source collection; see [Sources](../../sources/README.md). A Git clone should not inherit tens of megabytes of raw audio or proprietary session files by default.
- **Catalog and SHA manifests** are versioned here on GitHub. They are public metadata, not recordings.
- **Distribution** should use a deliberately published GitHub Release. Upload each of the **eleven individual MP3s** under the exact `release_asset_filename` from `catalog.json`; also attach the full checksum manifest and release notes. An optional album ZIP can coexist but does **not** enable per-track browser playback/download.
- The Portal's **Music options → Install soundtrack ZIP once** accepts a complete, verified **7-track legacy** or **11-track full** archive. Neither ZIP installer makes a GitHub upload.

The eleven-recording release-ready ZIP was prepared separately from the public Git checkout. Public standalone track URLs remain unverified pending the actual release upload.

## Attribution and publication boundaries

The Architect supplied these recordings and requested inclusion. Some ID3 metadata identifies Suno-assisted creation and the `mediocritasvt` creator account. For the original seven the Architect previously confirmed distribution eligibility; the later recordings' public distribution request is on record. **This is a user attribution/approval statement, not an independent rights audit.** Before publishing, the Architect should verify terms applying to every recording, release credits, and intended licensing.

Suggested credit: **MedioCritasVT / Conflux — music created with Suno** (subject to Architect review). Public listening/download does not automatically grant permission for unrelated remixing, synchronization, sublicensing or commercial use; no Creative Commons license is declared by this catalog.

## Future changes

The published Portal discovers official GitHub Release assets through the Release API. It neither creates release assets nor auto-plays music. Genre categorization, album sequencing, normalization, placement in Unreal, opening/closing-theme choices and canonical versions remain design and test work.

**Architect authority:** The Architect chooses what is distributed, included in the native game or accepted as final.
