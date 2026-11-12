# Conflux Portal — CachyOS deployment configuration (proposal)

**Status: configuration proposal only. Not approved, deployed, internet-exposed, or tested on CachyOS.**

This package offers a reproducible, **loopback-only preview** of the existing public static website at [`docs/index.html`](../../../docs/index.html). It deliberately reuses the already published Portal design instead of replacing it or launching a different application.

## Boundary

- **Public Portal:** a read-only website with links to approved public GitHub releases, books, and project information. This package serves **only** the repository's `docs/` directory.
- **Private Conflux Sanctum:** a separate future, authenticated Architect interface for GitHub review and private CachyOS services. **Not included or exposed here.**
- **Local `conflux/portal-app/`:** an experimental Python desktop/local launcher with local capabilities. **Never run it behind this public proxy.**
- **Home services and agent infrastructure:** Jellyfin, Immich, Kavita, Navidrome, SearXNG, Tailscale, VOS, RabbitMQ, SQLite, and the four-agent harness are not deployed by this package. See [SERVICE_ROADMAP.md](SERVICE_ROADMAP.md).

## Files

- `compose.yaml` — a single Caddy static-file container with a localhost-only port.
- `caddy/Caddyfile` — serves `docs/` on internal HTTP port 8080; no public listener or live administration.
- `.env.example` — optional, non-secret local preview settings; copy to untracked `.env` on the target machine.
- `reverse-proxy.example.Caddyfile` — **inactive example only** for eventual host-level HTTPS, requiring domain, DNS, firewall, and security review.
- `.gitignore` — keeps environment values and local state out of this directory's commits.

## Proposed later verification sequence (not executed)

1. The Architect reviews and accepts the GitHub configuration changes. Maintain a clean copy of existing CachyOS configurations and valuable data before any actual migration.
2. On a test machine with Podman and a working Compose provider, clone the repository. Enter `conflux/platforms/portal-deployment/`.
3. Copy `.env.example` to `.env` and check the local bind/port. Defaults are `127.0.0.1:8088`. No real domain or API key is required for a loopback preview.
4. Validate the Compose plan with `podman compose config` (subject to the installed provider). Review its output; only then choose whether to run `podman compose up -d`.
5. From that host, verify `http://127.0.0.1:8088/` loads the static page; review links, responsive layout, image requests, and logs. Confirm there is no access to the Python portal-app, private services, or private data.
6. Stop the test with `podman compose down`. This does **not** remove your existing data.
7. Public domain, HTTPS termination, host networking, automated startup, backups, and CachyOS integration require a **separate approval and acceptance test**. The example proxy file is not automatically installed.

**Container details:** `docker.io/library/caddy:2.11.9-alpine`; read-only `docs/` bind mount; ephemeral temporary/config directories; dropped Linux capabilities; container root filesystem read-only. It is not a full host-security review. The bind mount path is relative to this Compose file and assumes the repository's original folder structure is preserved.

## GitHub-first control

This is intended for a **separate proposal branch and draft pull request**. It does not modify the protected project by itself, launch a workflow, grant agent permissions, or deploy to CachyOS. Main-branch protections and agent-specific GitHub credentials must be checked before unattended write access is ever granted. Do not commit passwords, access tokens, OAuth secrets, certificates, database files, Tailscale auth keys, or private service configuration.

For reference, the existing source website has [publication notes](../../../docs/README.md). Source existing on GitHub is not evidence of a live hosted site.

## Open decisions for the Architect

- Which public domain and how DNS/TLS will terminate on the CachyOS server.
- Whether a host-installed reverse proxy or a dedicated container network is preferable.
- Which private services belong in Sanctum, and which should remain Tailscale-only.
- The preferred Podman Compose/Quadlet deployment strategy after inspecting the actual host.
- Whether and when to enable public hosting. **Do not infer approval from this draft.**
