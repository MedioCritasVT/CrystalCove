"""Opt-in, existing-service external-media bind-mount updates for Bazzite.

Never creates media paths, copies data, touches service state, changes container
images, enables Tailscale, or installs OS packages. One known Quadlet media
Volume line is changed only after a reviewed plan and physical desktop approval.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import shutil
import stat
import subprocess
import tempfile
import time
from pathlib import Path

import service_manager

# Exact service/target pairs allowlisted; do not accept arbitrary container paths.
TARGETS = {
    "jellyfin": ("/media",),
    "navidrome": ("/music",),
    "kavita": ("/books", "/comics", "/manga"),
}
PLANS: dict[str, dict] = {}
EXPIRES_SECONDS = 300
BACKUP_DIR = Path.home() / ".local" / "state" / "conflux-portal" / "quadlet-backups"


def _call(argv, timeout=25, max_chars=500):
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("System command unavailable or timed out") from exc
    return p.returncode, (p.stdout or p.stderr).strip()[:max_chars]


def _ensure_safe_source(value: str) -> tuple[Path, dict]:
    if not isinstance(value, str) or not value.startswith("/") or len(value) > 1000:
        raise ValueError("Choose an existing absolute path on an external mounted drive")
    # Quadlet Volume uses colon separators; control characters and whitespace
    # also require escaping we intentionally do not attempt here.
    if any(c in value for c in (":", "\n", "\r", "\x00")) or any(c.isspace() for c in value):
        raise ValueError("Mount paths containing whitespace or ':' are not yet supported; use a stable path without them")
    source = Path(value).resolve(strict=True)
    if not source.is_dir() or not os.access(source, os.R_OK | os.X_OK):
        raise ValueError("Selected folder is missing or not readable by this Bazzite user")
    if any(c in str(source) for c in (":", "\n", "\r", "\x00")) or any(c.isspace() for c in str(source)):
        raise ValueError("Resolved mount path contains unsupported characters")
    if source in (Path("/"), Path.home().resolve()) or source.is_relative_to(service_manager.ROOT.resolve()):
        raise ValueError("Select a dedicated external media folder, not your home or Conflux state")
    if not shutil.which("findmnt"):
        raise RuntimeError("findmnt is required to verify an existing external mount")
    rc, output = _call(["findmnt", "--json", "--target", str(source),
                         "--output", "TARGET,SOURCE,FSTYPE,OPTIONS"], timeout=10, max_chars=16000)
    if rc != 0:
        raise ValueError("Could not confirm a mounted filesystem at this path")
    try:
        entries = json.loads(output)["filesystems"]
        mount = entries[0]
        point = Path(mount["target"]).resolve(strict=True)
        fs_type = str(mount.get("fstype", ""))
    except (OSError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Unrecognized mount information; no changes made") from exc
    if (point == Path("/") or not source.is_relative_to(point)
            or fs_type.lower() in {"overlay", "tmpfs", "devtmpfs", "proc", "sysfs",
                                    "cgroup2", "squashfs", "autofs"}):
        raise ValueError("This folder is not verified as a separate mounted media filesystem")
    return source, {"mount_point": str(point), "filesystem": fs_type,
                    "mount_source": str(mount.get("source", "unknown"))}


def _unit_contents(service: str) -> tuple[Path, bytes]:
    if service not in TARGETS:
        raise ValueError("Unsupported media service")
    if not service_manager.on_bazzite() or os.geteuid() == 0:
        raise RuntimeError("Manage these services as the regular user on Bazzite")
    unit = service_manager.file_for(service)
    if unit.is_symlink() or not unit.is_file():
        raise ValueError("Conflux user Quadlet not found as a regular file; install first")
    if unit.stat().st_size > 32768:
        raise ValueError("Unexpectedly large Quadlet; inspect manually")
    original = unit.read_bytes()
    text = original.decode("utf-8")
    image = service_manager.SERVICES[service]["image"]
    if (f"ContainerName=conflux-media-{service}" not in text
            or f"Image={image}" not in text
            or f"PublishPort=127.0.0.1:{service_manager.SERVICES[service]['port']}:" not in text):
        raise ValueError("Existing Quadlet does not match the managed Conflux service; refusing rewrite")
    return unit, original


def _replace_media_volume(original: bytes, target: str, source: Path) -> tuple[bytes, str]:
    lines = original.decode("utf-8").splitlines(keepends=True)
    matched = []
    for i, line in enumerate(lines):
        value = line.rstrip("\r\n")
        if not value.startswith("Volume="):
            continue
        parts = value.removeprefix("Volume=").split(":")
        if len(parts) != 3:
            raise ValueError("Unexpected Volume syntax; edit manually")
        host, dest, flags = parts
        if dest == target:
            if "ro" not in flags.split(","):
                raise ValueError("Existing media mount is not read-only; refusing automatic rewrite")
            matched.append((i, host))
    if len(matched) != 1:
        raise ValueError("Expected exactly one media Volume for that service and target")
    position, previous = matched[0]
    new = f"Volume={source}:{target}:ro,nocreate\n"
    lines[position] = new
    return "".join(lines).encode("utf-8"), previous


def inspect(service: str, target: str, host_folder: str) -> dict:
    if service not in TARGETS or target not in TARGETS[service]:
        raise ValueError("Choose a known service and media destination")
    unit, old = _unit_contents(service)
    source, mount = _ensure_safe_source(host_folder)
    modified, previous = _replace_media_volume(old, target, source)
    # No plan is issued for an unchanged mount (including already updated units).
    changed = modified != old
    return {
        "service": service, "destination": target,
        "unit": str(unit), "current_host_folder": previous,
        "new_host_folder": str(source), "mount": mount,
        "preview": f"Volume={source}:{target}:ro,nocreate",
        "will_change": changed,
        "unit_hash": hashlib.sha256(old).hexdigest(),
        "notes": [
            "Changes exactly one media mount in this service's existing Quadlet.",
            "Keeps the existing /config or /data mount and all application databases.",
            "Does not copy media or make a second backup of external files.",
            "No SELinux relabel (:z/:Z), chmod, or chown is performed on the external disk.",
            "After approval, the selected service may restart; active sessions can be interrupted.",
            "If the device disconnects or the mount is unavailable, the service may fail to start.",
            "A timestamped backup of the original Quadlet is kept for manual recovery.",
            "Portal Git updates alone do not alter installed Quadlets or image versions.",
        ],
    }


def plan(service: str, target: str, host_folder: str) -> dict:
    PLANS.clear()
    info = inspect(service, target, host_folder)
    if info["will_change"]:
        token = secrets.token_urlsafe(24)
        PLANS[token] = {"expires": time.monotonic() + EXPIRES_SECONDS, "info": info}
        info["plan_token"] = token
    return info


def _atomic_write(path: Path, data: bytes, mode: int):
    fd, tmp = tempfile.mkstemp(prefix=".conflux-quadlet-", dir=str(path.parent))
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def apply(token: str) -> dict:
    if not isinstance(token, str) or len(token) > 100:
        raise ValueError("Invalid mount update token")
    saved = PLANS.pop(token, None)
    if saved is None or time.monotonic() > saved["expires"]:
        raise ValueError("Storage plan has expired; inspect the mounted path again")
    info = saved["info"]
    fresh = inspect(info["service"], info["destination"], info["new_host_folder"])
    if not fresh["will_change"] or fresh["unit_hash"] != info["unit_hash"] or fresh["preview"] != info["preview"]:
        raise ValueError("Quadlet or mount changed since preview; inspect again")
    unit, old = _unit_contents(info["service"])
    if hashlib.sha256(old).hexdigest() != info["unit_hash"]:
        raise ValueError("Quadlet changed during inspection")
    edited, _ = _replace_media_volume(old, info["destination"], Path(info["new_host_folder"]))
    service_name = f"conflux-media-{info['service']}.service"
    active_rc, _ = _call(["systemctl", "--user", "is-active", "--quiet", service_name], 10)
    was_active = active_rc == 0
    # The backup is of the small service definition, not its databases.
    if BACKUP_DIR.is_symlink():
        raise ValueError("Quadlet backup directory cannot be a symlink")
    BACKUP_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(BACKUP_DIR, 0o700)
    backup = BACKUP_DIR / (f"conflux-media-{info['service']}-{int(time.time())}-{secrets.token_hex(4)}.container.bak")
    with backup.open("xb") as dest:
        os.fchmod(dest.fileno(), 0o600)
        dest.write(old)
        dest.flush()
        os.fsync(dest.fileno())
    mode = stat.S_IMODE(unit.stat().st_mode)
    changed = False
    try:
        _atomic_write(unit, edited, mode)
        changed = True
        rc, msg = _call(["systemctl", "--user", "daemon-reload"], 20)
        if rc:
            raise RuntimeError("systemd reload failed: " + msg)
        if was_active:
            rc, msg = _call(["systemctl", "--user", "restart", service_name], 180)
            if rc:
                raise RuntimeError("Selected service restart failed: " + msg)
    except Exception as exc:
        rollback = "not needed"
        if changed:
            try:
                _atomic_write(unit, old, mode)
                _call(["systemctl", "--user", "daemon-reload"], 20)
                if was_active:
                    _call(["systemctl", "--user", "restart", service_name], 180)
                rollback = "original Quadlet restored; verify status"
            except Exception:
                rollback = "automatic restoration failed; use the preserved Quadlet backup"
        raise RuntimeError(f"Mount update failed: {exc}; {rollback}; backup: {backup}") from exc
    return {
        "updated": True, "service": info["service"], "destination": info["destination"],
        "host_folder": info["new_host_folder"], "unit_backup": str(backup),
        "restarted": was_active, "status": "Applied without changing application state or image version.",
    }
