#!/usr/bin/env python3
"""Conflux Portal: a Linux localhost-only launcher and project entrance."""
import json
import shutil
import time
import webbrowser
import os
import secrets
import re
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import game_locator
import music_library
from app_updater import UpdateManager, UpdateError
from theme_studio import ThemeStudio, StudioError
from portal_chat import ChatError, chat as assistant_chat, status as assistant_status
from portal_auth import AuthError, PortalConnections
from portal_prs import PullDesk, PullError
from urllib.parse import parse_qs
from install_desktop_launcher import install_desktop_launcher

ROOT = Path(__file__).resolve().parent
# Bundled, reviewable local service installer: never fetched from the network.
SERVICE_BUNDLE = ROOT.parent / "platforms" / "bazzite-service-bundle"
if SERVICE_BUNDLE.is_dir():
    sys.path.insert(0, str(SERVICE_BUNDLE))
    import service_manager as MEDIA_MIRROR
    import media_mounts as MEDIA_MOUNTS
else:
    MEDIA_MIRROR = None
    MEDIA_MOUNTS = None
MIRROR_LOCK = threading.Lock()
CONFIG = Path.home() / ".config" / "conflux-portal" / "apps.json"
TOKEN = secrets.token_urlsafe(24)
HOST = "127.0.0.1"
UPDATES = UpdateManager(ROOT.parents[1])
STUDIO = ThemeStudio(ROOT.parents[1])
CONNECTIONS = PortalConnections()
PULLS = PullDesk(STUDIO.repository, CONNECTIONS)
SUGGESTIONS = set()
SUGGESTIONS_LOCK = threading.Lock()

CATALOG = (
    {"id": "conflux-game", "name": "Conflux Game V0.1",
     "state": "published", "download_url": "/downloads"},
    {"id": "conflux-atelier", "name": "Conflux Atelier",
     "state": "bundled", "open_url": "/apps/atelier"},
    {"id": "conflux-ledger", "name": "Conflux Ledger",
     "state": "bundled", "open_url": "/apps/ledger"},
)


def configured_apps():
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        return [a for a in data if isinstance(a, dict) and
                isinstance(a.get("id"), str) and
                isinstance(a.get("executable"), str)]
    except (OSError, ValueError):
        return []


def apps_public():
    game = next((a for a in configured_apps() if a["id"] == "conflux-game"), None)
    path = Path(game["executable"]).expanduser() if game else None
    ready = bool(path and path.is_file() and os.access(path, os.X_OK))
    output = []
    for entry in CATALOG:
        if entry["id"] == "conflux-game":
            output.append({**entry, "installed": ready,
                           "action": "launch" if ready else "download"})
        else:
            output.append({**entry, "installed": True, "action": "open"})
    return output


def register_game(path):
    if not game_locator.valid_launcher(path):
        raise game_locator.LocateError("The selected PlayConflux.sh is missing or not executable.")
    with SUGGESTIONS_LOCK:
        if path not in SUGGESTIONS:
            raise game_locator.LocateError("Choose and inspect this folder using the Portal first.")
        SUGGESTIONS.clear()
    # Preserve unrelated configuration; fail rather than overwrite invalid data.
    if CONFIG.exists():
        try:
            entries = json.loads(CONFIG.read_text(encoding="utf-8"))
            if not isinstance(entries, list):
                raise ValueError("Not an array")
        except (OSError, ValueError) as exc:
            raise game_locator.LocateError("Existing apps.json is invalid; back it up and correct it first.") from exc
    else:
        entries = []
    entries = [a for a in entries if not (isinstance(a, dict) and a.get("id") == "conflux-game")]
    entries.append({"id": "conflux-game", "name": "Conflux Game V0.1", "executable": path})
    CONFIG.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=CONFIG.parent, prefix=".apps-",
                                         suffix=".json", delete=False) as handle:
            temp_path = Path(handle.name)
            os.chmod(temp_path, 0o600)
            json.dump(entries, handle, indent=2)
        os.replace(temp_path, CONFIG)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def confirm_mirror_install_on_host():
    """Independent physical-desktop confirmation: no remote-only installs."""
    message = (
        "Create NEW, separate Jellyfin, Kavita and Navidrome services on this "
        "Bazzite machine? This can download images and start containers. "
        "Existing media will NOT be copied, backed up or changed. "
        "Services will listen on localhost only."
    )
    program = shutil.which("kdialog")
    if program:
        cmd = [program, "--warningyesno", message, "--title", "Conflux service installer"]
    else:
        program = shutil.which("zenity")
        if not program:
            return False
        cmd = [program, "--question", "--title=Conflux service installer",
               "--text=" + message]
    try:
        return subprocess.run(cmd, capture_output=True, check=False,
                              timeout=90).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def confirm_mirror_storage_on_host(service, target, folder):
    """Explicit physical-desktop approval for a reviewed existing-service edit."""
    message = (
        f"Change ONLY the {service} media mount {target} to:\n{folder}\n\n"
        "The source must remain mounted. The selected service may restart. "
        "No media files, databases or application state will be moved or erased. "
        "The original Quadlet will be backed up. Proceed?"
    )
    program = shutil.which("kdialog")
    if program:
        cmd = [program, "--warningyesno", message, "--title",
               "Conflux existing media mount update"]
    else:
        program = shutil.which("zenity")
        if not program:
            return False
        cmd = [program, "--question", "--title=Conflux existing media mount update",
               "--text=" + message]
    try:
        return subprocess.run(cmd, capture_output=True, check=False, timeout=90).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def choose_mirror_media_folder():
    """Optional native folder picker; never creates or writes the selection."""
    if shutil.which("kdialog"):
        argv = ["kdialog", "--getexistingdirectory", str(Path.home()),
                "--title", "Choose a mounted external media folder"]
    elif shutil.which("zenity"):
        argv = ["zenity", "--file-selection", "--directory",
                "--title=Choose a mounted external media folder"]
    else:
        return {"cancelled": True, "detail": "No native picker; paste an absolute path from Dolphin."}
    try:
        result = subprocess.run(argv, capture_output=True, text=True,
                                timeout=100, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return {"cancelled": True}
    if result.returncode != 0:
        return {"cancelled": True}
    selected = result.stdout.strip()
    # Selection alone is not validation. The subsequent Plan operation
    # independently verifies a separate mounted filesystem.
    return {"cancelled": not bool(selected), "folder": selected}


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, path, mime):
        try:
            body = path.read_bytes()
        except OSError:
            return self.respond(404, {"error": "file-not-found"})
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("X-Content-Type-Options", "nosniff")
        if mime.startswith("text/html"):
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                "connect-src 'self'; media-src 'self' https://github.com https://*.githubusercontent.com; "
                "base-uri 'none'; form-action 'none'")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_music(self, path):
        """Serve only known, installed soundtrack MP3s with browser seeking."""
        asset = path
        size = asset.stat().st_size
        start, end, status = 0, size - 1, 200
        req = self.headers.get("Range")
        if req:
            match = re.fullmatch(r"bytes=(\d+)-(\d*)", req.strip())
            if not match:
                self.send_response(416)
                self.send_header("Content-Range", "bytes */%d" % size)
                self.end_headers()
                return
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else end
            if start >= size or end >= size or end < start:
                self.send_response(416)
                self.send_header("Content-Range", "bytes */%d" % size)
                self.end_headers()
                return
            status = 206
        self.send_response(status)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Accept-Ranges", "bytes")
        if status == 206:
            self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "private, max-age=3600")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        try:
            with asset.open("rb") as source:
                source.seek(start)
                remaining = end - start + 1
                while remaining:
                    chunk = source.read(min(65536, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        route = urlsplit(self.path).path
        if route in ("/", "/downloads"):
            return self.serve_file(ROOT / "index.html", "text/html; charset=utf-8")
        if route == "/familiars.css":
            return self.serve_file(ROOT / "familiars.css", "text/css; charset=utf-8")
        if route == "/theme_studio.css":
            return self.serve_file(ROOT / "theme_studio.css", "text/css; charset=utf-8")
        if route in ("/assistant", "/assistant/"):
            return self.serve_file(ROOT / "assistant.html", "text/html; charset=utf-8")
        if route == "/assistant_frame.js":
            return self.serve_file(ROOT / "assistant_frame.js", "text/javascript; charset=utf-8")
        if route == "/assistant_frame.css":
            return self.serve_file(ROOT / "assistant_frame.css", "text/css; charset=utf-8")
        if route == "/portal_chat.css":
            return self.serve_file(ROOT / "portal_chat.css", "text/css; charset=utf-8")
        if route == "/portal_chat.js":
            return self.serve_file(ROOT / "portal_chat.js", "text/javascript; charset=utf-8")
        if route == "/theme_studio.js":
            return self.serve_file(ROOT / "theme_studio.js", "text/javascript; charset=utf-8")
        if route == "/soundstage.css":
            return self.serve_file(ROOT / "soundstage.css", "text/css; charset=utf-8")
        if route == "/soundstage.js":
            return self.serve_file(ROOT / "soundstage.js", "text/javascript; charset=utf-8")
        if route == "/video_tour.js":
            return self.serve_file(ROOT.parents[1] / "docs" / "video_tour.js", "text/javascript; charset=utf-8")
        if route == "/video-tour/catalog.json":
            return self.serve_file(ROOT.parent / "video-tour" / "catalog.json", "application/json; charset=utf-8")
        if route == "/app.js":
            return self.serve_file(ROOT / "app.js", "text/javascript; charset=utf-8")
        if route == "/readme.js":
            return self.serve_file(ROOT / "readme.js", "text/javascript; charset=utf-8")
        if route == "/link_choice.js":
            return self.serve_file(ROOT / "link_choice.js", "text/javascript; charset=utf-8")
        if route == "/project/README.md":
            # Bundled README reflects the *installed* checkout, including
            # content updated through the explicit Git updater.
            return self.serve_file(ROOT.parents[1] / "README.md",
                                   "text/markdown; charset=utf-8")
        if route == "/music.js":
            return self.serve_file(ROOT / "music.js", "text/javascript; charset=utf-8")
        if route == "/soundtrack/catalog.json":
            return self.serve_file(ROOT.parent / "soundtrack" / "catalog.json",
                                   "application/json; charset=utf-8")
        if route == "/api/music/library":
            return self.respond(200, music_library.library())
        if route.startswith("/music/audio/"):
            asset = music_library.local_asset(route[len("/music/audio/"):])
            return self.serve_music(asset) if asset else self.respond(404, {"error": "unknown-track"})
        if route in ("/apps/atelier", "/apps/ledger"):
            file = "atelier.html" if route == "/apps/atelier" else "ledger.html"
            return self.serve_file(ROOT / "apps" / file, "text/html; charset=utf-8")
        if route == "/service-setup.js":
            return self.serve_file(ROOT / "service_setup.js",
                                   "text/javascript; charset=utf-8")
        if route in ("/auth/chatgpt/callback", "/auth/github/callback"):
            # Browser OAuth callback from the provider. State and nonce were
            # created only by an authorized POST from the locally served Portal.
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                return self.respond(403, {"error": "Local OAuth callback only."})
            kind = "chatgpt" if route.startswith("/auth/chatgpt") else "github"
            try:
                CONNECTIONS.finish(kind, parse_qs(urlsplit(self.path).query,
                                                   keep_blank_values=True))
                success = True
                label = kind.title() + " connected. Return to the Portal assistant."
            except AuthError:
                success = False
                label = "Sign-in could not complete. Return to the Portal and retry."
            data = ("<!doctype html><meta charset='utf-8'>"
                    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                    "<title>Conflux connection</title>"
                    "<style>body{font:1.1rem system-ui;max-width:36rem;margin:12vh auto;"
                    "padding:2rem;background:#151b2a;color:#f5f2f6}"
                    "a{color:#9cdec0}</style><h1>Conflux Portal</h1><p>"
                    + label + "</p><p>You can close this tab.</p>").encode("utf-8")
            self.send_response(200 if success else 400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if route in ("/api/pulls/list", "/api/pulls/detail"):
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                return self.respond(403, {"error": "Local PR desk only."})
            try:
                if route.endswith("/list"):
                    return self.respond(200, PULLS.list())
                num = parse_qs(urlsplit(self.path).query).get("number", [""])[0]
                return self.respond(200, PULLS.detail(num))
            except PullError as error:
                return self.respond(409, {"error": str(error)[:350]})
        if route == "/api/connections/status":
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                return self.respond(403, {"error": "Local connections only."})
            return self.respond(200, CONNECTIONS.status())
        if route == "/api/assistant/status":
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                return self.respond(403, {"error": "Use the local Portal to access the assistant."})
            return self.respond(200, assistant_status())
        if route == "/api/studio/status":
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                return self.respond(403, {"error": "Use the local Portal to inspect Studio."})
            return self.respond(200, STUDIO.status())
        if route == "/api/studio/theme":
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                return self.respond(403, {"error": "Use the local Portal to inspect themes."})
            try:
                from urllib.parse import parse_qs
                slug = parse_qs(urlsplit(self.path).query).get("slug", [""])[0]
                return self.respond(200, STUDIO.inspect_theme(slug))
            except StudioError as error:
                return self.respond(404, {"error": str(error)[:400]})
        if route == "/api/status":
            return self.respond(200, {
                "platform": sys.platform, "mode": "local-preview",
                "portal_root": str(ROOT),
                "vos": "not-connected", "apps": apps_public(),
                "picker_available": game_locator.picker_program() is not None,
                "launch_token": TOKEN,
            })
        return self.respond(404, {"error": "not-found"})

    def authorized(self):
        origin = self.headers.get("Origin", "")
        expected = "http://127.0.0.1:" + str(self.server.server_port)
        return origin == expected and self.headers.get("X-Conflux-Token") == TOKEN

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= 8192:
                return None
            data = json.loads(self.rfile.read(length))
            return data if isinstance(data, dict) else None
        except (OSError, TypeError, ValueError):
            return None

    def do_POST(self):
        route = urlsplit(self.path).path
        if route not in ("/api/music/install", "/api/music/install-public", "/api/launch", "/api/game/browse",
                         "/api/game/find", "/api/game/register",
                         "/api/updates/check", "/api/updates/apply",
                         "/api/updates/relaunch", "/api/desktop/install",
                         "/api/services/check", "/api/services/install",
                         "/api/services/storage/plan", "/api/services/storage/apply",
                         "/api/services/storage/browse",
                         "/api/studio/propose", "/api/studio/publish",
                         "/api/studio/preview", "/api/studio/main",
                         "/api/assistant/chat",
                         "/api/connections/start", "/api/connections/sign-out",
                         "/api/pulls/merge"):
            return self.respond(404, {"error": "not-found"})
        if not self.authorized():
            return self.respond(403, {"error": "forbidden"})
        if route == "/api/music/install-public":
            # Explicitly authenticated user gesture. The backend selects one
            # known GitHub Release asset; caller cannot supply arbitrary URLs.
            if self.headers.get("Content-Length") not in (None, "", "0"):
                return self.respond(400, {"error": "No request body expected."})
            try:
                return self.respond(200, music_library.install_from_public_release())
            except music_library.MusicError as exc:
                return self.respond(400, {"error": str(exc)})
            except (OSError, ValueError):
                return self.respond(400, {"error": "Could not install soundtrack into local music storage."})
        if route == "/api/music/install":
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 1 <= size <= music_library.MAX_ZIP_BYTES:
                    return self.respond(413, {"error": "The soundtrack ZIP must be smaller than 70 MB."})
                payload = self.rfile.read(size)
                return self.respond(200, music_library.install_release_zip(payload))
            except music_library.MusicError as exc:
                return self.respond(400, {"error": str(exc)})
            except (OSError, ValueError):
                return self.respond(400, {"error": "Could not install soundtrack ZIP."})
        body = self.read_json()
        if body is None:
            return self.respond(400, {"error": "invalid-request"})
        if route == "/api/pulls/merge":
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                return self.respond(403, {"error": "Local PR merge only."})
            try:
                return self.respond(200, PULLS.merge(body))
            except PullError as error:
                return self.respond(409, {"error": str(error)[:350]})
        if route in ("/api/connections/start", "/api/connections/sign-out"):
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                return self.respond(403, {"error": "Local account connection only."})
            try:
                kind = body.get("provider")
                if route.endswith("/start"):
                    callback = "http://127.0.0.1:" + str(self.server.server_port) + "/auth/" + str(kind) + "/callback"
                    return self.respond(200, CONNECTIONS.start(kind, callback))
                return self.respond(200, CONNECTIONS.sign_out(kind))
            except AuthError as error:
                return self.respond(409, {"error": str(error)[:300]})
        if route == "/api/assistant/chat":
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                return self.respond(403, {"error": "Use the local Portal to chat."})
            try:
                return self.respond(200, assistant_chat(body, connections=CONNECTIONS))
            except ChatError as error:
                return self.respond(400, {"error": str(error)[:400]})
        if route.startswith("/api/studio/"):
            # Studio never permits remote/Tailscale callers to mutate local Git.
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                return self.respond(403, {"error": "Use 127.0.0.1 to manage your Studio."})
            try:
                if route == "/api/studio/propose":
                    return self.respond(200, STUDIO.propose(body))
                if route == "/api/studio/publish":
                    return self.respond(200, STUDIO.publish(body))
                if route == "/api/studio/preview":
                    result = STUDIO.preview(body)
                else:
                    result = STUDIO.return_to_main(body)
                UPDATES.pending = None
                UPDATES.restart_needed = True
                return self.respond(200, result)
            except StudioError as error:
                return self.respond(409, {"error": str(error)[:400]})
        # Privileged service changes are desktop-local; the remote Tailscale
        # website may be viewed but cannot run host installer actions.
        if route in ("/api/services/check", "/api/services/install",
                      "/api/services/storage/plan", "/api/services/storage/apply",
                         "/api/services/storage/browse"):
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                return self.respond(403, {"error": "Use the local Bazzite Portal at 127.0.0.1 to manage services."})
            if MEDIA_MIRROR is None:
                return self.respond(501, {"error": "Bazzite bundle missing from this Portal checkout."})
            if not MIRROR_LOCK.acquire(blocking=False):
                return self.respond(409, {"error": "A service check or installation is already running."})
            try:
                if route == "/api/services/check":
                    return self.respond(200, MEDIA_MIRROR.issue_plan())
                if route == "/api/services/storage/browse":
                    return self.respond(200, choose_mirror_media_folder())
                if route == "/api/services/storage/plan":
                    if MEDIA_MOUNTS is None:
                        return self.respond(501, {"error": "Storage manager unavailable."})
                    return self.respond(200, MEDIA_MOUNTS.plan(
                        body.get("service"), body.get("destination"),
                        body.get("host_folder")))
                if route == "/api/services/storage/apply":
                    if MEDIA_MOUNTS is None:
                        return self.respond(501, {"error": "Storage manager unavailable."})
                    token = body.get("plan_token")
                    if (not isinstance(token, str)
                            or body.get("explicit_confirmation") != "APPLY READ-ONLY MEDIA MOUNT"):
                        return self.respond(400, {"error": "Review a current storage plan and approve it."})
                    pending = MEDIA_MOUNTS.PLANS.get(token)
                    if not pending:
                        return self.respond(409, {"error": "Storage plan missing or expired; inspect again."})
                    info = pending["info"]
                    if not confirm_mirror_storage_on_host(
                            info["service"], info["destination"], info["new_host_folder"]):
                        return self.respond(409, {"error": "Physical-desktop approval was declined."})
                    return self.respond(200, MEDIA_MOUNTS.apply(token))
                # A direct install call without a fresh token and explicit
                # user approval cannot proceed. Local dialog is an additional
                # safeguard against remote/proxied manipulation.
                plan_token = body.get("plan_token")
                confirmation = body.get("explicit_confirmation")
                if not isinstance(plan_token, str) or not isinstance(confirmation, str):
                    return self.respond(400, {"error": "A fresh plan and explicit confirmation are required."})
                if confirmation != "INSTALL NEW BAZZITE MIRROR":
                    return self.respond(400, {"error": "Confirmation was not accepted."})
                if not confirm_mirror_install_on_host():
                    return self.respond(409, {"error": "Installation was cancelled or no local confirmation dialog is available."})
                return self.respond(200, MEDIA_MIRROR.install(plan_token, confirmation))
            except (ValueError, RuntimeError, OSError) as error:
                return self.respond(409, {"error": str(error)[:400]})
            finally:
                MIRROR_LOCK.release()
        try:
            if route == "/api/updates/check":
                return self.respond(200, UPDATES.check())
            if route == "/api/updates/apply":
                return self.respond(200, UPDATES.apply())
            if route == "/api/desktop/install":
                entry = install_desktop_launcher()
                return self.respond(200, {"installed": True,
                                          "desktop_entry": entry})
            if route == "/api/updates/relaunch":
                if not UPDATES.restart_needed:
                    return self.respond(409, {"error": "Apply an update before relaunching."})
                # Spawn the newly checked-out Portal, which waits for this
                # server to release the stable port. Never execute a shell.
                state = Path.home() / ".local" / "state" / "conflux-portal"
                state.mkdir(parents=True, exist_ok=True)
                with (state / "portal.log").open("a", encoding="utf-8") as log:
                    child = subprocess.Popen(
                        [sys.executable, str(ROOT / "portal.py"), "--handoff"],
                        cwd=str(ROOT), start_new_session=True,
                        stdin=subprocess.DEVNULL, stdout=log,
                        stderr=subprocess.STDOUT, close_fds=True)
                self.respond(200, {"relaunching": True, "pid": child.pid})
                def stop_old_server():
                    time.sleep(0.2)
                    self.server.shutdown()
                threading.Thread(target=stop_old_server, daemon=True).start()
                return
            if route == "/api/game/browse":
                directory = game_locator.choose_folder()
                if directory is None:
                    return self.respond(200, {"cancelled": True})
                result = game_locator.scan_folder(directory)
                with SUGGESTIONS_LOCK:
                    SUGGESTIONS.clear()
                    SUGGESTIONS.update(c["path"] for c in result["candidates"] if c["ready"])
                return self.respond(200, result)
            if route == "/api/game/find":
                result = game_locator.scan_folder(body.get("directory"))
                with SUGGESTIONS_LOCK:
                    SUGGESTIONS.clear()
                    SUGGESTIONS.update(c["path"] for c in result["candidates"] if c["ready"])
                return self.respond(200, result)
            if route == "/api/game/register":
                path = body.get("path")
                if not isinstance(path, str):
                    return self.respond(400, {"error": "Choose a valid game path."})
                register_game(path)
                return self.respond(200, {"registered": True, "apps": apps_public()})
            if body.get("id") != "conflux-game":
                return self.respond(404, {"error": "game-not-configured"})
            games = [a for a in configured_apps() if a.get("id") == "conflux-game"]
            if len(games) != 1:
                return self.respond(404, {"error": "game-not-configured"})
            path = Path(games[0]["executable"]).expanduser().resolve(strict=True)
            if not path.is_file() or not os.access(path, os.X_OK):
                return self.respond(409, {"error": "game-unavailable"})
            subprocess.Popen([str(path)], cwd=str(path.parent), start_new_session=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, close_fds=True)
            return self.respond(200, {"started": True, "id": "conflux-game"})
        except UpdateError as exc:
            return self.respond(409, {"error": str(exc)})
        except game_locator.LocateError as exc:
            return self.respond(400, {"error": str(exc)})
        except (OSError, ValueError, RuntimeError):
            return self.respond(400, {"error": "request-failed"})

    def log_message(self, fmt, *args):
        # OAuth callbacks carry one-time codes; never print query strings.
        if self.path.startswith("/auth/"):
            print("Conflux OAuth callback handled", file=sys.stderr)
        else:
            print(fmt % args, file=sys.stderr)


if __name__ == "__main__":
    if not sys.platform.startswith("linux"):
        raise SystemExit("This Portal preview supports Linux only.")
    try:
        port = int(os.environ.get("CONFLUX_PORTAL_PORT", "8765"))
        if not 1024 <= port <= 65535:
            raise ValueError("port out of range")
    except ValueError:
        raise SystemExit("CONFLUX_PORTAL_PORT must be 1024–65535.")
    handoff = "--handoff" in sys.argv[1:]
    if handoff:
        deadline = time.monotonic() + 35
        while True:
            try:
                server = ThreadingHTTPServer((HOST, port), Handler)
                break
            except OSError as exc:
                if time.monotonic() >= deadline:
                    raise SystemExit("Relaunch failed to bind port %d: %s" % (port, exc))
                time.sleep(0.25)
    else:
        try:
            server = ThreadingHTTPServer((HOST, port), Handler)
        except OSError as exc:
            raise SystemExit("Could not bind Portal to 127.0.0.1:%d: %s" % (port, exc))
    if "--open-browser" in sys.argv[1:]:
        webbrowser.open("http://127.0.0.1:%d" % port)
    print("Conflux Portal: http://127.0.0.1:%d" % server.server_port, flush=True)
    print("Ctrl+C to stop; browser storage uses this exact port.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
