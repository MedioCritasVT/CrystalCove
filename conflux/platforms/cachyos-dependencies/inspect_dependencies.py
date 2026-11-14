#!/usr/bin/env python3
"""CachyOS dependency inventory for Conflux. Read-only; standard library only.

No installation, package synchronization, service control, container start,
network calls, or writing files is performed by this script.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import pwd
import shutil
import subprocess
import sys
from pathlib import Path

MIN_PYTHON = (3, 10)
REQUIREMENTS = {
    "static-portal": [
        ("podman", "podman", True, "Runs the existing loopback-only Caddy container."),
        ("podman-compose", "podman-compose", True, "Compose provider for portal-deployment/compose.yaml."),
        ("git", "git", False, "Optional: clone and update the source repository."),
        ("tailscale", "tailscale", False, "Optional: private connectivity; not needed for a local preview."),
    ],
    "local-portal": [
        ("python", "python3", True, "Runs the existing local Python Portal; version 3.10 or newer."),
        ("git", "git", False, "Enables the Portal Git-based Update workflow."),
        ("kdialog", "kdialog", False, "Optional KDE native folder picker; manual path entry also works."),
        ("zenity", "zenity", False, "Alternative optional graphical folder picker."),
    ],
    "media-foundation": [
        ("podman", "podman", True, "Container runtime for a future, separately approved server stack."),
        ("podman-compose", "podman-compose", True, "Compose provider for future service definitions."),
        ("git", "git", False, "Optional: versioned configuration checkout."),
        ("tailscale", "tailscale", False, "Optional: private access; preserve any existing configuration."),
    ],
}

def os_release(path: Path = Path("/etc/os-release")) -> dict[str, str]:
    """Read distro identification without executing shell commands."""
    result = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return result
    for line in lines:
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split("=", 1)
        if k in {"ID", "ID_LIKE", "PRETTY_NAME"}:
            result[k] = v.strip().strip('"').strip("'")
    return result

def installed_packages() -> tuple[set[str] | None, str | None]:
    """Read installed local pacman database; never sync repositories."""
    if shutil.which("pacman") is None:
        return None, "pacman not found"
    try:
        p = subprocess.run(
            ["pacman", "-Qq"], capture_output=True, text=True,
            timeout=12, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None, "pacman installed-package query unavailable"
    if p.returncode != 0:
        return None, "pacman installed-package query failed"
    return set(p.stdout.splitlines()), None

def requirement_status(pkg: str, binary: str, installed: set[str] | None,
                       binaries: set[str], python_version: tuple[int, int]) -> tuple[str, str]:
    """A package name alone does not prove its executable is usable."""
    if pkg == "podman-compose" and binary not in binaries and "docker-compose" in binaries:
        return "review", "docker-compose found; review Podman socket/provider configuration"
    if binary in binaries:
        if pkg == "python" and python_version < MIN_PYTHON:
            return "review", "Python 3.10+ required; this interpreter is older"
        return "available", "executable found"
    if installed is not None and pkg in installed:
        return "review", "pacman lists package, but expected executable is not on PATH"
    return "missing", "executable not found (no automatic installation attempted)"

def missing_required(rows: list[dict]) -> list[str]:
    """Only missing REQUIRED pacman packages may enter a proposed command."""
    return sorted({row["package"] for row in rows
                   if row["required"] and row["status"] == "missing"
                   and row["package"] not in {"kdialog", "zenity"}})

def inspect(profile: str, *, distro: dict[str, str] | None = None,
            installed: set[str] | None = None, pacman_error: str | None = None,
            binaries: set[str] | None = None,
            python_version: tuple[int, int] | None = None) -> dict:
    """Build a report; accepts injected facts for isolated unit tests."""
    if profile not in REQUIREMENTS:
        raise ValueError("unknown profile")
    distro = distro if distro is not None else os_release()
    if binaries is None:
        names = {req[1] for req in REQUIREMENTS[profile]}
        names.update({"pacman", "docker-compose", "systemctl"})
        binaries = {name for name in names if shutil.which(name)}
    if python_version is None:
        python_version = sys.version_info[:2]
    if installed is None and pacman_error is None:
        installed, pacman_error = installed_packages()
    rows = []
    for package, binary, required, why in REQUIREMENTS[profile]:
        status, detail = requirement_status(package, binary, installed, binaries, python_version)
        if installed is None and status == "missing":
            status, detail = "unknown", "pacman query unavailable; inspect packages manually"
        rows.append({"package": package, "binary": binary, "required": required,
                     "status": status, "detail": detail, "purpose": why})
    is_cachyos = distro.get("ID", "").lower() == "cachyos"
    missing = missing_required(rows)
    # Never provide a distro-specific package command without positive CachyOS
    # identification AND a successful local pacman inventory.
    install_preview = None
    if is_cachyos and installed is not None and missing:
        install_preview = "sudo pacman -Syu --needed " + " ".join(missing)
    notes = [
        "Read-only inspection only; this tool cannot install, update, or start anything.",
        "The proposed pacman command, when present, is display-only. Review it and arrange a maintenance window before running it.",
        "The existing static Portal uses a Caddy container; a host caddy package is not required.",
        "Do not run the local Python Portal or Sanctum behind the public reverse proxy.",
        "Jellyfin, Immich, Kavita, and Navidrome are future container deployments, not packages installed by this check.",
        "A green binary check is not proof that rootless Podman, volumes, firewall rules, persistence, or containers work.",
        "Do not commit machine reports containing identifiable details or private configuration to the public repo.",
    ]
    if not is_cachyos:
        notes.append("Host ID is not confirmed as CachyOS; package preview withheld.")
    if pacman_error:
        notes.append("Installed pacman inventory was unavailable: " + pacman_error)
    if "systemctl" not in binaries:
        notes.append("systemctl not found; systemd/Quadlet readiness needs separate review.")
    return {
        "tool": "Conflux CachyOS dependency preflight",
        "profile": profile,
        "host": {"os_id": distro.get("ID", "unknown"),
                 "id_like": distro.get("ID_LIKE", ""),
                 "name": distro.get("PRETTY_NAME", "unknown"),
                 "arch": platform.machine()},
        "checks": rows,
        "missing_required_packages": missing if installed is not None else [],
        "suggested_install_command_NOT_EXECUTED": install_preview,
        "notes": notes,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=list(REQUIREMENTS), default="static-portal")
    parser.add_argument("--json", action="store_true", help="Print structured results; never writes a file")
    args = parser.parse_args()
    if sys.version_info < MIN_PYTHON:
        print("Python 3.10 or newer is needed for this checker.", file=sys.stderr)
        return 2
    report = inspect(args.profile)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Conflux CachyOS dependency preflight — {args.profile}")
        print(f"Host: {report['host']['name']} ({report['host']['arch']})")
        print("No packages or services will be changed.\n")
        for row in report["checks"]:
            requirement = "required" if row["required"] else "optional"
            print(f"[{row['status']:<9}] {row['package']:<16} ({requirement}) — {row['purpose']}")
            if row["status"] in {"review", "unknown"}:
                print("             " + row["detail"])
        command = report["suggested_install_command_NOT_EXECUTED"]
        print("\nPotential command for manual review (NOT executed):")
        print("  " + (command or "None: no missing required packages verified, or host inventory unsupported"))
        print("\nImportant:")
        for line in report["notes"]:
            print(" - " + line)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
