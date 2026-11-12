# CachyOS service and interface roadmap (planning only)

**Source:** Architect's November 12, 2026 voice design. These are **requested or proposed services**, not claims of a functioning installation.

## First milestone — public Portal

- Serve the existing static `docs/` Portal, linking only to approved public GitHub resources.
- Repository configuration first; local preview second; CachyOS deployment and domain last.
- Read-only public content. No public write access to GitHub and no automatic Node decisions.
- Reverse proxy with HTTPS is a **separately reviewed follow-on**, not part of an activated configuration.

## Future private interface — Conflux Sanctum

- Private, front-facing Architect interface, hosted on CachyOS.
- GitHub review: proposals, pull requests, approval/rejection, release oversight.
- Private links or carefully authenticated integrations to server services, monitoring, VOS, and Nodes.
- Prefer Tailscale-only access initially; enforce permissions on the backend. Reusing visual components does **not** imply shared public/private backend privileges.

## Requested CachyOS services — later phases

| Component | Intended purpose | Proposed exposure |
| --- | --- | --- |
| Jellyfin | Video/media library | Private |
| Immich | Photo/video library | Private |
| Kavita | Books/comics library | Private |
| Navidrome | Music library | Private |
| SearXNG | Self-hosted search | Private by default; reassess separately |
| Tailscale | Secure remote network access | Host network layer, not a public web page |
| Reverse proxy | Route approved sites under named domains | Only explicit public routes |
| Portal | Player-facing public GitHub links and releases | Public after deployment approval |
| Sanctum | Architect's private web workspace | Private |
| Monitoring and backups | Health, recovery and continuity | Private / local |

Additional media-app databases, storage mounts, application images, login settings, ports, DNS names, and backup destinations are **not known**. Do not fabricate paths or credentials. Immich's documented multi-container dependencies require separate review.

## Later Conflux integration (not in this release)

VOS services, SQLite/RabbitMQ, local four-agent harness, private per-Node memories, and frontier/local Node collaboration are **separate engineering tracks**, not automatically part of this server package. GitHub is the version-controlled source; local persistent data and private memories must not be committed to the public repository.

**Design constraints:** preserve recoverable state; avoid rebuilding broken legacy folder layouts blindly; keep public and private systems separated; require Architect approval for production changes; verify backups, restart persistence, and access controls before migration.
