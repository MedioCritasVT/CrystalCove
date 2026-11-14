"""Conflux soundtrack: public release discovery and safe local one-time installation.

The public GitHub API is used read-only. MP3s are only streamed when they have
actually been published or explicitly installed from a verified release ZIP.
"""
import hashlib
import io
import json
import os
import re
import tempfile
import threading
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT.parent / "soundtrack" / "catalog.json"
CHECKSUMS_PATH = ROOT.parent / "soundtrack" / "RELEASE_SHA256SUMS.txt"
RELEASE_TAG = "conflux-soundtrack-v0.1"
API = "https://api.github.com/repos/MedioCritasVT/CrystalCove/releases/tags/" + RELEASE_TAG
RELEASE_URL = "https://github.com/MedioCritasVT/CrystalCove/releases/tag/" + RELEASE_TAG
RELEASE_PREFIX = "https://github.com/MedioCritasVT/CrystalCove/releases/download/" + RELEASE_TAG + "/"
MAX_ZIP_BYTES = 70 * 1024 * 1024
MAX_MP3_BYTES = 18 * 1024 * 1024
REMOTE_CACHE_SECONDS = 240

_cache_lock = threading.Lock()
_cached_assets = None
_cached_at = 0.0
_cached_error = "not-checked"


class MusicError(Exception):
    pass


def music_directory():
    xdg = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))).expanduser()
    return xdg / "conflux-portal" / "soundtrack"


def metadata():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def checksums():
    result = {}
    for line in CHECKSUMS_PATH.read_text(encoding="utf-8").splitlines():
        sha, name = line.split("  ", 1)
        if not re.fullmatch(r"[a-f0-9]{64}", sha):
            raise MusicError("Invalid official checksum manifest.")
        result[name] = sha
    return result


def expected_assets():
    return {
        version["release_asset_filename"]
        for track in metadata()["tracks"]
        for version in track["variants"]
        if version.get("publication_status") == "staged_pending_upload"
    }


def local_asset(name):
    if name not in expected_assets():
        return None
    path = music_directory() / name
    if path.is_symlink() or not path.is_file():
        return None
    return path


def public_release_assets():
    global _cached_assets, _cached_at, _cached_error
    with _cache_lock:
        if _cached_assets is not None and time.monotonic() - _cached_at < REMOTE_CACHE_SECONDS:
            return _cached_assets, _cached_error
    request = urllib.request.Request(
        API, headers={"Accept": "application/vnd.github+json",
                      "User-Agent": "Conflux-Portal/0.1"})
    error = None
    found = {}
    try:
        with urllib.request.urlopen(request, timeout=4) as response:
            obj = json.load(response)
        if obj.get("draft") or obj.get("tag_name") != RELEASE_TAG:
            error = "release-not-public"
        else:
            for asset in obj.get("assets", []):
                name, url = asset.get("name"), asset.get("browser_download_url")
                if (name in expected_assets() and isinstance(url, str) and
                        url == RELEASE_PREFIX + name and asset.get("size", 0) > 0):
                    found[name] = url
            if not found:
                error = "release-has-no-matching-audio"
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, ValueError, TimeoutError):
        error = "release-not-yet-reachable"
    with _cache_lock:
        _cached_assets, _cached_at, _cached_error = found, time.monotonic(), error
    return found, error


def library():
    # The files already installed on this machine work without an internet connection.
    public, remote_error = public_release_assets()
    tracks = []
    available = 0
    local = 0
    remote = 0
    for track in metadata()["tracks"]:
        variants = []
        for v in track["variants"]:
            name = v["release_asset_filename"]
            installed = local_asset(name) is not None
            url = ("/music/audio/" + name if installed else public.get(name))
            source = "local" if installed else "published" if url else "unavailable"
            if url:
                available += 1
                local += int(installed)
                remote += int(not installed)
            variants.append({
                "id": v["id"], "filename": name, "duration_seconds": v.get("duration_seconds"),
                "source": source, "url": url,
                "download_url": public.get(name),
            })
        tracks.append({"id": track["id"], "title": track["title"],
                       "variants": variants})
    return {"tracks": tracks, "available": available, "local": local,
            "published": remote, "remote_status": remote_error,
            "release_url": RELEASE_URL, "music_off_by_default": True}


def install_release_zip(payload):
    if not isinstance(payload, (bytes, bytearray)) or len(payload) > MAX_ZIP_BYTES or not payload:
        raise MusicError("Choose the Conflux soundtrack ZIP (70 MB maximum).")
    allowed = checksums()
    expected = expected_assets()
    if set(allowed) != expected:
        raise MusicError("The soundtrack release checksum list is incomplete.")
    try:
        archive = zipfile.ZipFile(io.BytesIO(payload))
    except (zipfile.BadZipFile, ValueError) as exc:
        raise MusicError("This isn't a valid soundtrack ZIP.") from exc
    data_dir = music_directory()
    data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    staged = []
    with archive, tempfile.TemporaryDirectory(prefix=".conflux-music-", dir=data_dir) as staging:
        names = set()
        for entry in archive.infolist():
            name = entry.filename
            if name not in expected:
                continue  # Release notes/checksums are harmless and ignored.
            if name in names or "/" in name or "\\" in name or entry.is_dir():
                raise MusicError("Repeated or invalid audio entry in the archive.")
            names.add(name)
            if entry.file_size > MAX_MP3_BYTES:
                raise MusicError("Audio file exceeds the per-track size limit.")
            destination = Path(staging) / name
            digest = hashlib.sha256()
            total = 0
            try:
                with archive.open(entry) as src, destination.open("xb") as dst:
                    while chunk := src.read(65536):
                        total += len(chunk)
                        if total > MAX_MP3_BYTES:
                            raise MusicError("An audio entry exceeds the upload limit.")
                        digest.update(chunk)
                        dst.write(chunk)
            except (OSError, RuntimeError, ValueError, zipfile.BadZipFile) as exc:
                raise MusicError("The soundtrack ZIP contains an unreadable file.") from exc
            if digest.hexdigest() != allowed[name]:
                raise MusicError("Checksum mismatch for " + name + ". No files were installed.")
            staged.append((destination, data_dir / name))
        if not staged:
            raise MusicError("The selected ZIP contains no recognized Conflux soundtrack MP3s.")
        if len(staged) != len(expected):
            raise MusicError("The archive is incomplete; expected all %d verified recordings." % len(expected))
        for src, dst in staged:
            if dst.is_symlink():
                raise MusicError("A soundtrack destination is a symlink. Installation stopped.")
        for src, dst in staged:
            os.replace(src, dst)
            dst.chmod(0o600)
    return {"installed": len(staged), "directory": str(data_dir)}
