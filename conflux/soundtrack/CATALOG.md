# Conflux Soundtrack — working release catalog

**Status (November 14, 2026):** Ten recordings are inventoried across nine compositions. Seven original recordings across six compositions have full verified fingerprints and a staging package; the Architect subsequently supplied three additional recordings on November 13, 2026. Their titles and original filenames are recorded here, but their MP3 bytes were not accessible for hashing or release preparation in this pass. The Architect previously confirmed distribution eligibility for the original seven, but all publication still requires a real audio upload; the three new titles await their own verification. **A catalog entry is not a public download.**

The [machine-readable catalog](catalog.json) keeps all ten recordings separate. The [seven-track SHA-256 manifest](RELEASE_SHA256SUMS.txt) applies to the original staged audio only and must **not** be presented as verification of the three later recordings.

| Composition | Received version(s) | Duration | Public file status |
| --- | --- | ---: | --- |
| Awareness transcends that which it is aw… | Source filename `(2)`; display title truncated | 3:35 | Staged for upload |
| Call Me Through the Mountain | Provided take | 4:03 | Staged for upload |
| Ghost in the Circuit Chapel | Provided take | 3:56 | Staged for upload |
| Ritual in the Circuit | Provided take | 3:24 | Staged for upload |
| The Weight of the World | Provided take | 3:00 | Staged for upload |
| **Sacrament of Oath** | **Take 1** / **Take 2** | **2:25 / 2:26** | **Both staged separately** |
| Who Gave You the Crown? | `Who Gave You the Crown_.mp3` | Not verified here | Cataloged; MP3 upload pending |
| Little Adventurer | `Little Adventurer.mp3` | Not verified here | Cataloged; MP3 upload pending |
| LITTLE GODS IN WHITE GLOVES | `LITTLE GODS IN WHITE GLOVES.mp3` | Not verified here | Cataloged; MP3 upload pending |

## Credits and provenance

The recordings' MP3 metadata identifies **Suno-assisted generation** and, on six files, the artist account `mediocritasvt`. The user supplied the audio and confirmed having checked distribution rights on November 10, 2026. No Suno subscription invoices were supplied to this repository, and no independent legal conclusion is claimed.

Suggested public credit: **MedioCritasVT / Conflux — music created with Suno**. Public listening and downloading do **not** automatically grant visitors rights to relicense, remix, synchronize, or commercially redistribute the tracks. No Creative Commons license is declared here.

## Publication steps

The proposed GitHub Release tag is `conflux-soundtrack-v0.1`. Do not claim a release or any individual audio file exists publicly until its binary has been uploaded and verified. The Architect has a downloadable staging package containing each asset under a stable ASCII filename, checksum file, and release notes.

To publish, open the GitHub Releases interface, choose **Draft a new release**, use the proposed tag, and attach the **verified MP3 files individually**, plus the appropriate checksums/release notes. The three later tracks require new hashes and separate approval before being labeled verified. Avoid a ZIP-only upload if browser streaming is desired. Publish only after reviewing the public credits and scope. Verify each asset's SHA-256 hash or download it back and compare before marking it live.

Both the local Portal and the static website can discover **publicly released** MP3 asset URLs automatically using the official GitHub Release API; no manual catalog URL copy is required. Each asset must match the expected filename and release tag. Visitors press **Music On** to play. The Architect may also use **Install soundtrack ZIP once…** for permanent playback on their own machine before GitHub release publication. These steps do not silently upload audio or start playback on page load.

## Version and game boundaries

Neither Sacrament of Oath take is automatically promoted to canonical. Game placement, looping, in-game triggers, credits and loudness normalization remain separate design/testing work. Catalog inclusion is not an implementation or release approval for the Unreal build.

**Architect authority:** The Architect selects which recordings are distributed, used in-game, or designated final.
