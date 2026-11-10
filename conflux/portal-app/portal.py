#!/usr/bin/env python3
"""Conflux Portal local Linux preview. Python standard library only."""
import json
import os
import secrets
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
CONFIG = Path.home() / ".config" / "conflux-portal" / "apps.json"
TOKEN = secrets.token_urlsafe(24)
HOST = "127.0.0.1"

def configured_apps():
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        return [x for x in data if isinstance(x, dict) and isinstance(x.get("id"), str)
                and isinstance(x.get("name"), str) and isinstance(x.get("executable"), str)]
    except (OSError, ValueError):
        return []

def apps_public():
    out = []
    for a in configured_apps():
        path = Path(a["executable"]).expanduser()
        out.append({"id": a["id"], "name": a["name"],
                    "available": path.is_file() and os.access(path, os.X_OK)})
    return out

class Handler(BaseHTTPRequestHandler):
    def respond(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == "/":
            body = (ROOT / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'none'")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif route == "/app.js":
            body = (ROOT / "app.js").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif route == "/api/status":
            self.respond(200, {"platform": sys.platform, "mode": "local-preview",
                               "vos": "not-connected", "apps": apps_public(),
                               "launch_token": TOKEN})
        else:
            self.respond(404, {"error": "not-found"})

    def do_POST(self):
        if urlsplit(self.path).path != "/api/launch":
            return self.respond(404, {"error": "not-found"})
        origin = self.headers.get("Origin", "")
        expected = "http://127.0.0.1:" + str(self.server.server_port)
        if origin != expected or self.headers.get("X-Conflux-Token") != TOKEN:
            return self.respond(403, {"error": "forbidden"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > 2048:
                return self.respond(400, {"error": "invalid-request"})
            data = json.loads(self.rfile.read(size))
            app_id = data.get("id")
            matches = [a for a in configured_apps() if a["id"] == app_id]
            if len(matches) != 1:
                return self.respond(404, {"error": "app-not-configured"})
            path = Path(matches[0]["executable"]).expanduser().resolve(strict=True)
            if not path.is_file() or not os.access(path, os.X_OK):
                return self.respond(409, {"error": "app-unavailable"})
            # Only an executable explicitly listed in the user's local configuration.
            subprocess.Popen([str(path)], cwd=str(path.parent), start_new_session=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, close_fds=True)
            return self.respond(200, {"started": True, "id": app_id})
        except (OSError, ValueError, TypeError, KeyError):
            return self.respond(400, {"error": "launch-failed"})

    def log_message(self, fmt, *args):
        print(fmt % args, file=sys.stderr)

if __name__ == "__main__":
    if not sys.platform.startswith("linux"):
        raise SystemExit("This development preview supports Linux only.")
    server = ThreadingHTTPServer((HOST, 0), Handler)
    print("Conflux Portal: http://127.0.0.1:%d" % server.server_port, flush=True)
    print("Ctrl+C to stop. Local access only.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
