# Conflux Soundtrack — verified working release catalog

**Status (2026-11-14):** **Eleven supplied MP3 recordings across ten distinct compositions** have been verified by exact SHA-256 checksum. Seven match the [original manifest](RELEASE_SHA256SUMS.txt) byte-for-byte; the four further recordings (three from the first Architect EP and *Silicon Saints*) now appear in the [complete eleven-recording manifest](RELEASE_SHA256SUMS_FULL.txt). Both *Sacrament of Oath* takes remain independent versions.

**Audio is not yet published as individual GitHub Release assets.** The Portal and static website now show the full catalog but only activate direct MP3 downloads when GitHub reports an actual corresponding asset. Uploading an asset is a separate publication step, not implied by catalog inclusion.

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

## Publish the complete soundtrack in one upload

The fastest public distribution is the single verified album archive **`Conflux_Soundtrack_11_Recordings_Release_Ready.zip`** (57,270,992 bytes / roughly 55 MiB). The user already has a local copy in their `SourceFiles/Songs` working collection. This public asset should be uploaded to a **GitHub Release**, not committed into the Git clone.

1. In the [CrystalCove Releases page](https://github.com/MedioCritasVT/CrystalCove/releases), choose **Draft a new release**.
2. Choose **Create new tag** `conflux-soundtrack-v0.1` targeting `main`. Use the title **Conflux Soundtrack — 11 Recordings**.
3. Attach the existing complete ZIP from the local computer. Keep its filename exactly `Conflux_Soundtrack_11_Recordings_Release_Ready.zip`. Add credits and the conditions under which the Architect authorizes distribution. Publish the release.
4. Verify that the ZIP appears as an asset on the published Release page. Both the Portal and the static website will then discover the public ZIP and offer **Download the complete 11-recording soundtrack ZIP** automatically, without Git or an account. **Do not claim publication before the asset is visible.**

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
