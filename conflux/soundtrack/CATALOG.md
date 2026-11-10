# Conflux Soundtrack — working release catalog

**Status (November 10, 2026):** Seven actual MP3 recordings received and identified, covering six compositions. **The Architect states they checked and cleared distribution eligibility.** This is an attributable rights confirmation, not an independently audited license. The MP3 binaries have **not yet been uploaded to a GitHub release**; they are not available for public streaming from this repository.

The [machine-readable catalog](catalog.json) keeps each take separate. The [full SHA-256 checksums](RELEASE_SHA256SUMS.txt) allow the eventual uploaded release assets to be verified against the received source files.

| Composition | Received version(s) | Duration | Public file status |
| --- | --- | ---: | --- |
| Awareness transcends that which it is aw… | Source filename `(2)`; display title truncated | 3:35 | Staged for upload |
| Call Me Through the Mountain | Provided take | 4:03 | Staged for upload |
| Ghost in the Circuit Chapel | Provided take | 3:56 | Staged for upload |
| Ritual in the Circuit | Provided take | 3:24 | Staged for upload |
| The Weight of the World | Provided take | 3:00 | Staged for upload |
| **Sacrament of Oath** | **Take 1** / **Take 2** | **2:25 / 2:26** | **Both staged separately** |

## Credits and provenance

The recordings' MP3 metadata identifies **Suno-assisted generation** and, on six files, the artist account `mediocritasvt`. The user supplied the audio and confirmed having checked distribution rights on November 10, 2026. No Suno subscription invoices were supplied to this repository, and no independent legal conclusion is claimed.

Suggested public credit: **MedioCritasVT / Conflux — music created with Suno**. Public listening and downloading do **not** automatically grant visitors rights to relicense, remix, synchronize, or commercially redistribute the tracks. No Creative Commons license is declared here.

## Publication steps

The proposed GitHub Release tag is `conflux-soundtrack-v0.1`. Do not claim this release exists until the seven audio binaries have actually been uploaded. The Architect has a downloadable staging package containing each asset under a stable ASCII filename, checksum file, and release notes.

To publish, open the GitHub Releases interface, choose **Draft a new release**, use the proposed tag, and attach the **seven MP3 files individually**, plus the checksums/release notes. Avoid a ZIP-only upload if browser streaming is desired. Publish only after reviewing the public credits and scope. Verify each asset's SHA-256 hash or download it back and compare before marking it live.

Once real asset URLs are verified, add each public URL to its corresponding `catalog.json` variant and enable public playback in the Portal. The current Portal player supports **local file selection with an opt-in music toggle**. It never automatically uploads the user's audio or starts music on load.

## Version and game boundaries

Neither Sacrament of Oath take is automatically promoted to canonical. Game placement, looping, in-game triggers, credits and loudness normalization remain separate design/testing work. Catalog inclusion is not an implementation or release approval for the Unreal build.

**Architect authority:** The Architect selects which recordings are distributed, used in-game, or designated final.
