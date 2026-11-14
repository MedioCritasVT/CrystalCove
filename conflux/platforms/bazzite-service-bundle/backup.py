#!/usr/bin/env python3
"""Stop-first, local configuration backup for fresh Conflux mirror only."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import tarfile
from pathlib import Path
from service_manager import ROOT, SUPPORTED

def stopped():
    for name in SUPPORTED:
        cmd = ["systemctl", "--user", "is-active", "--quiet",
               "conflux-media-" + name + ".service"]
        p = subprocess.run(cmd, capture_output=True, check=False, timeout=10)
        if p.returncode == 0:
            raise RuntimeError(name + " is running; stop all mirror services before backup")

def create_backup(destination: Path):
    destination = destination.expanduser().resolve()
    state = ROOT / "state"
    if not state.is_dir():
        raise RuntimeError("No local mirror state directory exists")
    if destination == ROOT or ROOT in destination.parents:
        raise RuntimeError("Backup destination must be outside mirror data")
    stopped()
    if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
        raise RuntimeError("Invalid backup destination")
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(destination, 0o700)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = destination / ("conflux-mirror-state-" + stamp + ".tar.gz")
    if archive.exists():
        raise RuntimeError("Backup filename exists; no overwrite allowed")
    # Write only new archive with private permissions. Do not follow symlinks
    # out of the state tree or archive passwords from unrelated home folders.
    fd = os.open(archive, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as raw:
            with tarfile.open(fileobj=raw, mode="w:gz") as tar:
                for path in sorted(state.rglob("*")):
                    if path.is_symlink():
                        raise RuntimeError("Refusing symlink in service state: " + str(path))
                    tar.add(path, arcname=str(path.relative_to(ROOT)),
                            recursive=False)
        checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
        checkfile = archive.with_suffix(archive.suffix + ".sha256")
        with checkfile.open("x", encoding="utf-8") as out:
            out.write(checksum + "  " + archive.name + "\n")
        os.chmod(checkfile, 0o600)
        return {"archive": str(archive), "sha256": checksum,
                "media_included": False, "destination": str(destination)}
    except Exception:
        archive.unlink(missing_ok=True)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, help="Existing or new private backup folder outside service data")
    args = parser.parse_args()
    print(json.dumps(create_backup(Path(args.destination)), indent=2))
