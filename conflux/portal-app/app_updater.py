"""Conflux Portal's opt-in, non-destructive update path.

Checks GitHub's public main over HTTPS. Never resets, rebases, stashes, forces
or overwrites local work. Git's own fast-forward safeguards remain authoritative.
"""
import os
import re
import shutil
import subprocess
import threading
from pathlib import Path

REPOSITORY = "https://github.com/MedioCritasVT/CrystalCove.git"
TRUSTED_ORIGINS = (
    re.compile(r"https://github\.com/MedioCritasVT/CrystalCove(?:\.git)?/?", re.I),
    re.compile(r"git@github\.com:MedioCritasVT/CrystalCove(?:\.git)?", re.I),
    re.compile(r"ssh://git@github\.com/MedioCritasVT/CrystalCove(?:\.git)?/?", re.I),
)
MAX_OUTPUT = 900


class UpdateError(Exception):
    """Non-destructive failure to inspect or update the local checkout."""


class UpdateManager:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.lock = threading.RLock()
        self.pending = None
        self.restart_needed = False

    def git(self, *args, timeout=20, allow_exit=()):
        if not shutil.which("git"):
            raise UpdateError("Git isn't installed. The Portal can still open your apps.")
        try:
            p = subprocess.run(
                ["git", "-C", str(self.root), *args],
                stdin=subprocess.DEVNULL, capture_output=True, text=True,
                timeout=timeout,
                env={**os.environ, "GIT_TERMINAL_PROMPT": "0",
                     "GCM_INTERACTIVE": "never"},
                check=False)
        except subprocess.TimeoutExpired as e:
            raise UpdateError("Git timed out. Check your internet connection.") from e
        except OSError as e:
            raise UpdateError("Could not start Git: " + str(e)) from e
        if p.returncode and p.returncode not in allow_exit:
            error = (p.stderr or p.stdout or "Git returned an error").strip()
            raise UpdateError(error[-MAX_OUTPUT:])
        return p.stdout.strip(), p.returncode

    def verify_checkout(self):
        actual, _ = self.git("rev-parse", "--show-toplevel")
        if Path(actual).resolve() != self.root:
            raise UpdateError("Portal must run from its own CrystalCove Git clone.")
        origin, _ = self.git("remote", "get-url", "origin")
        if not any(pattern.fullmatch(origin.strip()) for pattern in TRUSTED_ORIGINS):
            raise UpdateError(
                "This checkout's origin is not the official CrystalCove GitHub repository. "
                "Automatic updating is disabled to protect your files.")
        branch, _ = self.git("symbolic-ref", "--quiet", "--short", "HEAD",
                             allow_exit=(1,))
        if not branch:
            raise UpdateError("Detached HEAD checkout. Automatic updates are disabled.")
        main_sha, _ = self.git("rev-parse", "--verify", "refs/heads/main")
        return {"branch": branch, "main": main_sha}

    def check(self):
        with self.lock:
            current = self.verify_checkout()
            # Read official public GitHub over HTTPS, not an SSH key that might
            # prompt for a passphrase from a headless desktop launcher.
            self.git("fetch", "--no-tags", "--quiet", REPOSITORY,
                     "refs/heads/main", timeout=75)
            target, _ = self.git("rev-parse", "--verify", "FETCH_HEAD")
            _, is_ancestor = self.git(
                "merge-base", "--is-ancestor", current["main"], target,
                allow_exit=(1,))
            if is_ancestor:
                self.pending = None
                raise UpdateError(
                    "Your local main has changes that cannot be fast-forwarded. "
                    "Nothing was touched. Review your branch history first.")
            count, _ = self.git("rev-list", "--count",
                                current["main"] + ".." + target)
            changed_files, _ = self.git("diff", "--name-only", current["main"], target)
            need_update = target != current["main"]
            needs_switch = current["branch"] != "main"
            self.pending = {"target": target, **current}
            return {
                "status": "available" if need_update else
                          ("switch" if needs_switch else "current"),
                "current_branch": current["branch"], "local": current["main"][:10],
                "remote": target[:10], "commits": int(count),
                "changed_files": len(changed_files.splitlines()) if changed_files else 0,
                "needs_switch": needs_switch, "can_apply": need_update or needs_switch,
                "detail": (
                    "Updates are ready; click Update to fast-forward main."
                    if need_update else
                    "Main is current. Update can switch you back from the review branch."
                    if needs_switch else
                    "You're already up to date on main."
                ),
            }

    def apply(self):
        with self.lock:
            if not self.pending:
                raise UpdateError("Click Check for Updates before applying anything.")
            checked = self.pending
            current = self.verify_checkout()
            if current != {"branch": checked["branch"], "main": checked["main"]}:
                self.pending = None
                raise UpdateError("The checkout changed since checking. Check again first.")
            # This is a normal safe switch; Git refuses a checkout that would
            # overwrite dirty files. No force, reset, stash, or clean is used.
            if current["branch"] != "main":
                self.git("switch", "main", timeout=25)
            before, _ = self.git("rev-parse", "HEAD")
            if before != checked["main"]:
                self.pending = None
                raise UpdateError("Main changed during the branch switch. Check again.")
            if before != checked["target"]:
                # This Git operation refuses divergence and rejects local
                # modifications that would be overwritten.
                self.git("merge", "--ff-only", checked["target"], timeout=60)
            after, _ = self.git("rev-parse", "HEAD")
            self.pending = None
            if after != checked["target"]:
                raise UpdateError("Git did not reach the expected commit. Inspect status.")
            self.restart_needed = before != after or current["branch"] != "main"
            return {
                "updated": True, "commit": after[:10],
                "relaunch": self.restart_needed,
                "detail": "Official main is current. Your unrelated local files were not reset.",
            }
