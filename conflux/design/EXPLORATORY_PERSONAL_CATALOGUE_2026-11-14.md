# Exploratory — A personally shaped, self-updating catalogue

**Status:** Architect-originated exploratory concept, 2026-11-14. Not approved for development, not a feature currently shipped, not a data-collection instruction. **The Architect retains decisions about scope, implementation and release.**

## Core insight

> A structural system can exist without implying use.

Conflux's present approach separates the presence of a module, interface and source record from the act of executing it. The Architect extends this beyond a game library: each individual could shape a distinct portal/interface that feels like an expressive fingerprint **to its owner**, without allowing the application to fingerprint its user for tracking.

The example is a full, self-updating catalogue of available games, their platform/service relationships, metadata, and news about open-source opportunities (especially tools, modding, engines, compatibility work and other opportunities important to the Architect).

## Possible catalogue fields (no scanning authorized)

| Area | Example fields | Confidence and use boundary |
| --- | --- | --- |
| Identity | game ID, title, aliases, developer/publisher, release version | Source and retrieval date accompany every fact; distinguish similarly named products |
| Distribution | storefronts, launchers, service/provider, OS/architecture, URL | Listing ≠ ownership, entitlement or permission to install |
| Local experience | user-added executable path, installed status, build hash | Explicit user consent; local-only unless exported; never enumerate home folders by default |
| Compatibility | Linux/Bazzite/Steam Deck status, Proton/Wine notes, DRM/anti-cheat caveats | Cite testing context, date and platform; show unknown when unverified |
| Creative opportunities | open-source engine/library, modding APIs, SDKs, community projects, source-available status | Source-available ≠ open-source; licensing and provenance required |
| News | publisher announcements, project changelogs, relevant vulnerabilities and open opportunities | Date, publisher URL, relevance reason, freshness and user-selected feeds |
| User's expression | collections, themes, layouts, custom metadata and filters | Never derive a marketing identifier or treat expression as account identity |

## Possible architecture if approved later

```text
local personal interface
    ├── source adapters (each OFF unless user connects it)
    │   ├── optional public open game catalog
    │   ├── Steam/itch/other authorized provider integrations
    │   ├── opted-in local manifests (no whole-home scan)
    │   └── chosen news / open-source project feeds
    ├── normalized local metadata cache
    │   └── per-field source, timestamp, license, verification, freshness
    ├── view presets and individually editable presentation
    ├── export/import and user control
    └── optional updater (checks metadata; does not install or launch)
```

Keep **catalogue refresh**, **client software update**, **game update**, **metadata suggestion**, **download**, **launch** and **publication** as separate consent boundaries. The presence of an adapter is not its activation. An interface can work offline. Disconnected services should remain visibly disconnected rather than being invented.

## Design tension worth preserving

An expressive, individualized interface is a creative ambition, not a behavioral surveillance system. If a user likes a game, modifies a dashboard or has a unique layout, that combination should not secretly become a cross-service identifier. Prefer on-device manifests, permissioned imports, no tracking, reproducible app behavior, explainable provenance and a simple way to disable/delete a source.

**Next decision if the Architect authorizes a prototype:** choose a limited example feed and an editable source/metadata schema; create a local-only read-only mock interface before automating any discovery.

Related: [Source and distribution boundaries](../../sources/README.md), [Portal source](../portal-app/README.md), [Git/ZIP/player test matrix](../../docs/PLAYER_FIRST_RUN_TEST_STATUS_2026-11-13.md).
