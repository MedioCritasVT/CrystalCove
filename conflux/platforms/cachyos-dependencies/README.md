# CachyOS dependency preflight — Conflux server build

**Status: read-only inspection and manual package plan. Not an installer, release, server migration, or proof of service readiness.**

This is the next piece of the proposed Conflux server distribution. It targets the **CachyOS host** without altering the existing Bazzite Portal, Tailscale test environment, server configuration, containers, or media libraries.

## Run a check on CachyOS

In your existing CrystalCove checkout:

```bash
cd conflux/platforms/cachyos-dependencies
python3 inspect_dependencies.py --profile static-portal
```

Other available profiles:

```bash
python3 inspect_dependencies.py --profile media-foundation
python3 inspect_dependencies.py --profile local-portal
python3 inspect_dependencies.py --profile static-portal --json
python3 -m unittest -v test_inspect_dependencies.py
```

**What it does:** reads `/etc/os-release`, checks which executable names are on `PATH`, and queries locally installed packages using `pacman -Qq`. It does **not** run `pacman -S`, `sudo`, `podman`, `systemctl`, `tailscale`, downloads, network requests, or any service configuration. No files are written. JSON is printed to stdout if requested; redirect it to a private file only if you choose.

**What the profiles mean:**

| Profile | Required host pieces | Optional considerations |
| --- | --- | --- |
| `static-portal` | `podman`, `podman-compose` | `git` for clones; `tailscale` for private tests |
| `local-portal` | `python3` version 3.10+ | `git` updater; `kdialog` or `zenity` picker |
| `media-foundation` | `podman`, `podman-compose` | `tailscale` private access, `git` source checkout |

The actual public website currently has a separate [loopback-only Caddy Compose proposal](../portal-deployment/README.md). The host doesn't need a `caddy` package for that container-based approach.

The media-foundation profile checks **container tooling only**: it intentionally does *not* prescribe system packages or container images for Jellyfin, Immich, Kavita, or Navidrome. Those require a separate volume/database/backup plan and service-by-service acceptance testing. Immich in particular cannot safely be represented as a lone generic container.

## How missing packages are handled

On a positively identified CachyOS host with a successful local pacman inventory, the output includes a **display-only** `sudo pacman -Syu --needed ...` command containing *only missing required packages*. It is never executed. Optional packages are excluded. A present executable counts as available; an installed package without its expected executable is flagged for review. If `docker-compose` exists instead of `podman-compose`, the checker reports a manual provider/socket review rather than asserting compatibility.

CachyOS uses a rolling-release package manager, so an actual package transaction requires review of the full system update, existing services, backups, and a maintenance window. Do not blindly copy a command from a report onto a running server.

If Python is missing, this checker cannot run; first inspect `python3 --version`, `pacman -Q python`, and your CachyOS package state manually. The script does not try to bootstrap itself.

## What this does *not* validate

- Whether Podman actually runs rootless containers, or whether a Compose provider can start the Caddy service;
- Firewall, HTTPS, routing, DNS, storage mounts, privileges, SELinux/AppArmor, or systemd persistence;
- NVIDIA/Immich acceleration or separate model-serving infrastructure;
- Existing Jellyfin, Immich, Kavita, Navidrome, SearXNG, or Tailscale configurations and backups;
- Any public exposure of the Portal, private Sanctum access, or migration of existing services.

**Next test:** run the checker on the actual CachyOS host, review the exact output, then decide which missing dependencies (if any) are worth installing. Only after that can we validate the already proposed static Portal stack locally; migration remains a separate, opt-in decision.

## Package and runtime references

- [CachyOS FAQ — package manager and update practices](https://wiki.cachyos.org/cachyos_basic/faq/)
- [CachyOS post-install maintenance](https://wiki.cachyos.org/configuration/post_install_setup/)
- [ArchWiki — Podman and rootless/Compose considerations](https://wiki.archlinux.org/title/Podman)
- [Podman Compose provider semantics](https://man.archlinux.org/man/podman-compose.1.en)
- [CachyOS podman-compose package](https://packages.cachyos.org/package/extra/any/podman-compose)
