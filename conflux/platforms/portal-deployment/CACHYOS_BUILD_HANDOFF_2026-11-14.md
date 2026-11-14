# Conflux Portal / CachyOS build handoff

**Checkpoint:** 2026-11-14  
**Disposition:** PAUSED by Architect's request — preserve source and plans; do not deploy, install packages, migrate data, expose services, or modify running machines.

## Grounded accomplishments

- The **local Python Conflux Portal** on Bazzite is already running in the Architect's environment. The Architect supplied a mobile Firefox screenshot showing the Portal rendered over an existing **private Tailscale connection**, including Threshold, responsive navigation, Philosophy, About Arch, and the soundtrack controls with a track selected. This is user-supplied **visual evidence of page rendering and network reachability**, not proof of playback, persistence, login security, complete navigation coverage, or production deployment. The screenshot and private tailnet address have **not** been placed in the public repository.
- Philosophy and About Arch have separate Portal rooms and static `docs/` source pages. The philosophy gained a practical magic-circle/workspace comparison and a step-by-step illustrative example of how creative questions become Portal surfaces. These source changes were committed to `main`; public GitHub Pages hosting remains unverified.
- A distinct **CachyOS public static-site proposal** already exists at `conflux/platforms/portal-deployment/` using a read-only Caddy container with a host-loopback bind. This has **not** been executed or verified on CachyOS. The Python local Portal should not be exposed to the internet through that proxy.
- The **read-only CachyOS dependency preflight** was committed to `conflux/platforms/cachyos-dependencies/` (source publication commit `65a9398f5aa293f686c421cba90b794e1a845d62`). It inventories package availability for `static-portal`, `local-portal`, and `media-foundation`, and may print a display-only candidate pacman command. Its source and test cases were reviewed for obvious nonmutating behavior; **tests have not yet run on the actual CachyOS host**. An inventory is not an install or a security audit.

## What remains (not authorized to execute yet)

1. **CachyOS preflight:** on the actual target, inspect `python3`, `pacman`, Podman/Compose, disk and storage considerations, existing workloads, and read-only checker output. Inspect before proposing any installation. Keep exact host details and diagnostics private.
2. **Rehearse the public static site locally:** after review of any needed packages, validate the existing Compose plan and run a separately authorized loopback-only Caddy preview. Check `docs/` links, mobile layouts, image delivery, and ordinary web accessibility. Public DNS/HTTPS is a later approval.
3. **Design the server distribution without migration:** inventory the existing Jellyfin, Immich, Kavita, Navidrome, SearXNG and associated storage, databases, access needs, configuration and backups. Draft reproducible per-service container/Quadlet definitions and restore instructions **after** the inventory; do not guess paths, secrets, or versions. Immich's database and other dependencies must be treated explicitly. Maintain private-by-default access.
4. **Separate the private Sanctum:** design its own authentication, permissions and Tailscale-only initial access. Do not put private applications, model tool endpoints, Podman sockets or media admin interfaces behind the public Portal.
5. **Optional future dependency assistant:** make the Portal present relevant Bazzite/CachyOS prerequisite checks, propose only missing packages, and ask explicit approval before installations. This is design direction, **not a shipped installer**.
6. **Only after independent acceptance:** consider a deployment plan, service persistence, authenticated access, backup/restore validation and eventually server migration. The existing Bazzite Portal and CachyOS media installations must remain unchanged until authorized.

## Boundary and decision

- **Current target:** build/source preservation only.
- **Bazzite:** existing local Portal + private Tailscale mobile viewing; no need to rebuild this experience as a prerequisite.
- **CachyOS:** future target for public website, separate private Sanctum and potentially a reproducible media stack. Deployment not performed.
- **Evidence:** a GitHub source commit is proof of source publication, not execution on the target host. The screenshot is observational evidence, not a complete acceptance test.
- **Approval:** Architect chooses if and when to resume. The next safe move is to run only the read-only CachyOS preflight, then review its results.

## Pointers

- [CachyOS preflight](../cachyos-dependencies/README.md)
- [Static website deployment proposal](README.md)
- [Service separation and roadmap](SERVICE_ROADMAP.md)
- [Portal philosophy](../../../docs/philosophy.html)
- [About Arch](../../../docs/about-arch.html)
