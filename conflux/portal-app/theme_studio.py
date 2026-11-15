"""Opt-in, bounded Portal theme studio.

An agent may propose a COLOR PALETTE, not arbitrary code. Publishing creates
a separate review branch in the active local checkout and pushes that branch
using the user's existing Git credentials. No automatic merge or host commands
are delegated to the model.
"""
import json
import os
import re
import secrets
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

FIELDS = ("bg", "side", "surface", "ink", "muted", "line",
          "amber", "violet", "blue", "green")
DEFAULT = {
    "bg": "#111522", "side": "#151b2a", "surface": "#202638",
    "ink": "#f5f2f6", "muted": "#c4c4d3", "line": "#53556b",
    "amber": "#e9bf84", "violet": "#c2a4f3", "blue": "#84bff3",
    "green": "#9cdec0",
}
NODES = {"medio", "ratio", "nexus", "specula", "limen"}
COLORS = re.compile(r"#[0-9a-fA-F]{6}\Z")
TEXTURES = {"none", "parchment", "constellation", "grid", "weave"}
GITHUB_REMOTE = re.compile(
    r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)"
    r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?\Z", re.I)
SLUG = re.compile(r"[a-z][a-z0-9-]{0,39}\Z")


class StudioError(Exception):
    pass


def contrast(a, b):
    def lum(h):
        values = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]
        values = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
                  for v in values]
        return sum(w * v for w, v in zip((.2126, .7152, .0722), values))
    x, y = sorted((lum(a), lum(b)))
    return (y + .05) / (x + .05)


def validate_palette(palette):
    if not isinstance(palette, dict) or set(palette) != set(FIELDS):
        raise StudioError("A theme must contain exactly the ten supported color fields.")
    if any(not isinstance(v, str) or not COLORS.fullmatch(v) for v in palette.values()):
        raise StudioError("All theme colors must be six-digit hexadecimal values.")
    palette = {key: palette[key].lower() for key in FIELDS}
    if contrast(palette["ink"], palette["bg"]) < 4.5:
        raise StudioError("Text and background contrast must reach 4.5:1.")
    if contrast(palette["ink"], palette["surface"]) < 4.5:
        raise StudioError("Text and card contrast must reach 4.5:1.")
    if contrast(palette["muted"], palette["bg"]) < 4.5:
        raise StudioError("Muted text must remain readable against the background.")
    return palette


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")[:40]
    if not SLUG.fullmatch(slug):
        raise StudioError("Give the theme a name using letters or numbers.")
    return slug


def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$", "", text, flags=re.I)
    try:
        return json.loads(text)
    except ValueError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise StudioError("The agent did not produce valid JSON.")
        try:
            return json.loads(text[start:end+1])
        except ValueError as error:
            raise StudioError("The agent did not produce valid JSON.") from error


def ask_agent(provider, node, instruction):
    persona = {
        "medio": "welcome, comfort, and legible rhythm",
        "ratio": "precision, clarity, and contrast",
        "nexus": "coherent structure and navigation",
        "specula": "observation and visible distinctions",
        "limen": "gentle transitions and continuity",
    }[node]
    prompt = (
        "You are creating only a ten-color CSS palette for the Conflux Portal. "
        "Use the " + node.title() + " design lens: " + persona + ". "
        "Return ONLY a JSON object with keys: bg, side, surface, ink, muted, "
        "line, amber, violet, blue, green. Every value must be a #RRGGBB hex "
        "color. Use a readable DARK theme; main text and muted text must "
        "contrast well against backgrounds. Do not include code, scripts, "
        "Markdown or additional keys. User request: " + instruction
    )
    try:
        if provider == "ollama":
            endpoint = "http://127.0.0.1:11434/api/generate"
            payload = {"model": os.getenv("CONFLUX_STUDIO_OLLAMA_MODEL", "qwen3.5:4b"),
                       "prompt": prompt, "stream": False, "format": "json"}
            headers = {"Content-Type": "application/json"}
        elif provider == "openai":
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise StudioError("OPENAI_API_KEY is not set on the local Portal host.")
            endpoint = "https://api.openai.com/v1/responses"
            payload = {"model": os.getenv("CONFLUX_STUDIO_OPENAI_MODEL", "gpt-5-mini"),
                       "input": prompt, "max_output_tokens": 700}
            headers = {"Content-Type": "application/json", "Authorization": "Bearer " + key}
        else:
            raise StudioError("Choose a supported provider.")
        request = Request(endpoint, data=json.dumps(payload).encode("utf-8"),
                          headers=headers, method="POST")
        with urlopen(request, timeout=55) as response:
            raw = response.read(100_000)
        reply = json.loads(raw)
        if provider == "ollama":
            message = reply.get("response", "")
        else:
            parts = [c.get("text", "") for o in reply.get("output", [])
                     for c in o.get("content", []) if c.get("type") == "output_text"]
            message = "".join(parts) or reply.get("output_text", "")
        return validate_palette(extract_json(message))
    except StudioError:
        raise
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
        # Never echo model provider HTTP response bodies or credentials.
        raise StudioError("The selected AI provider was unavailable or returned an invalid response.") from error


class ThemeStudio:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.lock = threading.RLock()
        self.pending = None
        self.published = None

    def git(self, *args, cwd=None, timeout=35):
        try:
            result = subprocess.run(["git", "-C", str(cwd or self.root), *args],
                                    capture_output=True, text=True, timeout=timeout,
                                    stdin=subprocess.DEVNULL,
                                    env={**os.environ, "GIT_TERMINAL_PROMPT": "0",
                                         "GCM_INTERACTIVE": "never"}, check=False)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise StudioError("Git is not available or did not respond.") from error
        if result.returncode:
            # Do not echo arbitrary Git credential-helper diagnostics.
            raise StudioError("Git could not complete the requested safe operation. "
                              "Check branch state, Git credentials, and permissions.")
        return result.stdout.strip()

    def repository(self):
        actual = self.git("rev-parse", "--show-toplevel")
        if Path(actual).resolve() != self.root:
            raise StudioError("Start Portal from its own Git repository checkout.")
        remote = self.git("remote", "get-url", "origin")
        match = GITHUB_REMOTE.fullmatch(remote)
        if not match:
            raise StudioError("The origin remote must be a normal github.com HTTPS or SSH URL.")
        return match.group(1)

    def status(self):
        try:
            repo = self.repository()
            branch = self.git("branch", "--show-current")
            return {"repository": repo, "branch": branch or "(detached)",
                    "git_ready": True,
                    "published_branch": (self.published or {}).get("branch", "")}
        except StudioError:
            return {"repository": None, "branch": None, "git_ready": False,
                    "published_branch": ""}
    
    def propose(self, body):
        with self.lock:
            name = str(body.get("name", ""))[:80].strip()
            slug = slugify(name)
            node = body.get("agent")
            if node not in NODES:
                raise StudioError("Choose one of the five design Nodes.")
            provider = body.get("provider")
            instruction = body.get("instruction", "")
            if not isinstance(instruction, str) or len(instruction) > 1200:
                raise StudioError("Keep the design request within 1,200 characters.")
            if provider == "manual":
                palette = validate_palette(body.get("palette"))
            elif provider in ("ollama", "openai"):
                if not instruction.strip():
                    raise StudioError("Describe the theme for the selected agent.")
                palette = ask_agent(provider, node, instruction)
            else:
                raise StudioError("Choose Manual, Ollama, or OpenAI API.")
            texture = body.get("texture", "none")
            if not isinstance(texture, str) or texture not in TEXTURES:
                raise StudioError("Unrecognized Portal background texture.")
            ticket = secrets.token_urlsafe(22)
            self.pending = {"ticket": ticket, "name": name, "slug": slug,
                            "palette": palette, "texture": texture,
                            "agent": node, "provider": provider,
                            "created": time.monotonic()}
            return {"ticket": ticket, "name": name, "slug": slug,
                    "palette": palette, "texture": texture,
                    "agent": node, "provider": provider,
                    "tests": ["Supported fields only", "Hex colors only",
                              "Readable text contrast", "Known texture"], "published": False}

    def publish(self, body):
        with self.lock:
            proposal = self.pending
            if not proposal or body.get("ticket") != proposal["ticket"]:
                raise StudioError("Prepare and review a fresh theme before publishing.")
            if time.monotonic() - proposal["created"] > 1800:
                self.pending = None
                raise StudioError("Theme proposal expired; prepare it again.")
            if body.get("confirmation") != "PUBLISH REVIEWED THEME":
                raise StudioError("Explicit publication approval is required.")
            repo = self.repository()
            branch = "conflux/studio-" + proposal["slug"][:22] + "-" + secrets.token_hex(4)
            relative = "conflux/portal-app/studio-themes/" + proposal["slug"] + ".json"
            payload = json.dumps({
                "name": proposal["name"], "agent": proposal["agent"],
                "palette": proposal["palette"], "texture": proposal["texture"], "schema": 1,
            }, indent=2, ensure_ascii=False) + "\n"
            # Build from HEAD inside an isolated worktree so unsaved local user
            # changes cannot be staged, committed, stashed, reset or overwritten.
            with tempfile.TemporaryDirectory(prefix="conflux-studio-") as area:
                worktree = Path(area) / "review"
                added = False
                try:
                    self.git("worktree", "add", "--detach", str(worktree), "HEAD")
                    added = True
                    self.git("switch", "-c", branch, cwd=worktree)
                    destination = worktree / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    # Refuse symlinked ancestor directories in the checkout.
                    # A source tree must not redirect palette writes outside the
                    # disposable worktree, even if its content is untrusted.
                    if not destination.parent.resolve().is_relative_to(worktree.resolve()):
                        raise StudioError("Theme directory escapes the review worktree.")
                    if destination.exists() or destination.is_symlink():
                        raise StudioError("Theme name already exists in the checkout; choose another.")
                    destination.write_text(payload, encoding="utf-8")
                    self.git("add", "--", relative, cwd=worktree)
                    self.git("commit", "-m", "Portal Studio: add reviewed theme " + proposal["slug"],
                             cwd=worktree)
                    sha = self.git("rev-parse", "HEAD", cwd=worktree)
                    self.git("push", "--set-upstream", "origin",
                             "HEAD:refs/heads/" + branch, cwd=worktree, timeout=75)
                finally:
                    if added:
                        self.git("worktree", "remove", "--force", str(worktree))
            self.pending = None
            self.published = {"branch": branch, "sha": sha, "repo": repo,
                              "path": relative}
            return {"published": True, "branch": branch, "commit": sha[:12],
                    "path": relative,
                    "review_url": "https://github.com/" + repo +
                                  "/compare/main..." + branch + "?expand=1",
                    "note": "A review branch was pushed. Nothing was merged into main."}

    def preview(self, body):
        with self.lock:
            published = self.published
            if not published or body.get("branch") != published["branch"]:
                raise StudioError("Publish a theme before previewing its branch.")
            if body.get("confirmation") != "PREVIEW REVIEW BRANCH":
                raise StudioError("Approve the explicit local branch switch.")
            if self.repository().lower() != published["repo"].lower():
                raise StudioError("The repository changed since publication.")
            self.git("switch", published["branch"])
            # Git switch refuses to overwrite conflicting local modifications.
            return {"branch": published["branch"], "relaunch": True,
                    "detail": "Review branch checked out safely. Relaunch to load its files."}

    def return_to_main(self, body):
        with self.lock:
            if body.get("confirmation") != "RETURN TO MAIN":
                raise StudioError("Approve the branch switch explicitly.")
            self.repository()
            self.git("switch", "main")
            return {"branch": "main", "relaunch": True,
                    "detail": "Returned to local main without resetting files."}

    def inspect_theme(self, slug):
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            raise StudioError("Invalid theme name.")
        path = self.root / "conflux" / "portal-app" / "studio-themes" / (slug + ".json")
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 4096:
            raise StudioError("Theme file not found in this checkout.")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise StudioError("Cannot read the theme file.") from error
        if data.get("schema") != 1 or data.get("agent") not in NODES:
            raise StudioError("Theme version or Node identity is unsupported.")
        texture = data.get("texture", "none")
        if texture not in TEXTURES:
            raise StudioError("Invalid theme background texture.")
        return {"name": data.get("name"), "agent": data.get("agent"),
                "palette": validate_palette(data.get("palette")),
                "texture": texture, "schema": 1, "loaded": True}
