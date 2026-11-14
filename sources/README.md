# Conflux Sources — editable originals, not automatic services

**Status:** developer-facing structure proposal and character-familiar implementation source, 2026-11-14. The Architect decides what is made public, included in a release, or adopted as canonical.

**Sources** encompasses **music masters, artwork and reference panels, authored code, modifiable game assets, developer tools and local/private work**. It is not synonymous with the playable build, a running AI agent, or a player's installed library. A file's presence does **not** authorize execution, installation, synchronization, scanning, reuse or publishing.

## Two levels: source and distribution

- **Source**: an editable original, a record of provenance, or material needed to reproduce an asset. Some sources can be public; some must remain local and private.
- **Distribution**: an independently packaged output (game build, Portal, MP3 release asset, public gallery) with explicit approvals. Downloading the Portal does not imply downloading every raw source, and a Git clone should not require large audio/game downloads.
- **Runtime**: the player's locally selected installation, saves, settings, browser Ledger or agent configuration. It is not automatically imported into Git.

### Initial source directory map

```text
~/Conflux/
├── CrystalCove/                        # versioned public Git checkout
│   ├── sources/                        # source guidelines, schemas and chibi design
│   │   ├── character-familiars/        # visual implementation references + style spec
│   │   ├── music/                      # manifests and processing instructions
│   │   ├── artwork/                    # references and format notes
│   │   ├── developer/                  # reproducible configs and examples
│   │   └── private/                    # optional local-only, gitignored; never expected
│   ├── conflux/concept-art/reference-art/ # already-published reference plates
│   ├── conflux/soundtrack/             # public metadata + checksums, not MP3 binaries
│   ├── conflux/portal-app/             # runnable local Portal source
│   └── docs/                           # optional static public web source
└── SourceFiles/                        # OPTIONAL recommended private working originals,
    ├── music/masters/                  # uncompressed masters, licensed source recordings
    ├── artwork/                        # Blender .blend, layered art, sketches, textures
    ├── developer/                      # local toolchains, experiments
    ├── exports/                        # staged release candidates before approval
    └── private/                        # passwords, private notes, sensitive work
```

The folder `~/Conflux/SourceFiles/` is **outside the public Git checkout**. This is the safest default for private and large editable originals. Alternatively, `sources/private/` and other specifically ignored paths are reserved inside a clone for local-only work. Neither path is created or read by the Portal automatically. Do **not** add sensitive, proprietary or unlicensed source files to a public branch.

## Mapping existing work without relocating it

| Source type | Current established public location | Release/distribution boundary |
| --- | --- | --- |
| Node character panels | [Reference art index](../conflux/concept-art/reference-art/README.md) | Chibi styling uses named references, but approval of a panel and final cartoon likeness are separate |
| Portal code, tests, manual | [Portal app](../conflux/portal-app/) | Git version controls the Portal and linked docs; standalone Unreal builds remain separate |
| Recorded soundtrack metadata | [Catalog](../conflux/soundtrack/catalog.json), [11-recording SHA-256 manifest](../conflux/soundtrack/RELEASE_SHA256SUMS_FULL.txt) | Actual MP3s belong in explicit GitHub Release assets or optional local-only masters; catalogs never create download rights |
| Concept media / historical captures | [Concept art collection](../conflux/concept-art/README.md) | Large archives are Release assets; current reference plates already live in the public repo |
| VOS / four-agent harness | [Platform index](../conflux/platforms/README.md) | Optional experiments; separate runtime private memory and credentials must not be placed in Git |

## Reproducing the modular approach

A developer may copy the **structure**, write their own manifest, link their own game/library sources and implement their own Portal. They should not assume Conflux assets are licensed for reuse merely because source files are visible. The user should be able to control their own interface independently of any specific store, engine or service.

Future idea (not implemented here): a **personal, updateable catalogue** of games and applications across launchers, storefronts and open-source repositories. Each entry can record identity, platform, service, provenance, version, accessibility, install status and relevant development/open-source news. The interface is a user's *expression of their selections and priorities*, not a fingerprinting or tracking system. Collection must be **opt-in per source**; support local-only mode, export/import and deletion; distinguish **available, installed, owned, and playable**; do not infer licensing or ownership from a detected executable. News is attributed with source, date and freshness and cannot execute packages.

**Core principle:** *The structure may be present without its features being enabled.* A directory, catalog entry, manifest or companion icon is not permission to act.
