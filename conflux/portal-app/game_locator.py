"""Conflux Portal: bounded, user-invoked Linux game-folder discovery.

The Portal never scans the whole home directory or executes files discovered here.
Only a user-selected folder is inspected for PlayConflux.sh, and a separate
confirmation is required to register that file as a possible launch target.
"""
from pathlib import Path
import os
import shutil
import subprocess

LAUNCHER = "PlayConflux.sh"
MAX_DEPTH = 4
MAX_DIRECTORIES = 450
MAX_CANDIDATES = 12


class LocateError(Exception):
    pass


def picker_program():
    for program in ("kdialog", "zenity"):
        found = shutil.which(program)
        if found:
            return (program, found)
    return None


def choose_folder():
    """Use a native desktop folder picker. No shell, no terminal commands."""
    picker = picker_program()
    if picker is None:
        raise LocateError("No native folder picker found (kdialog/zenity). Paste the folder path instead.")
    name, executable = picker
    if name == "kdialog":
        argv = [executable, "--getexistingdirectory", str(Path.home()),
                "--title", "Find your extracted Conflux game"]
    else:
        argv = [executable, "--file-selection", "--directory",
                "--title=Find your extracted Conflux game"]
    try:
        proc = subprocess.run(argv, text=True, capture_output=True,
                              timeout=180, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LocateError("The desktop folder chooser could not finish: " + str(exc)) from exc
    if proc.returncode != 0 or not proc.stdout.strip():
        return None  # User cancelled; this is not an error.
    return proc.stdout.strip().splitlines()[0]


def scan_folder(directory):
    """Return only explicitly selected roots and launchers, never arbitrary files."""
    if not isinstance(directory, str) or not directory.strip() or len(directory) > 4096:
        raise LocateError("Choose a folder or enter its absolute path.")
    original = Path(directory.strip()).expanduser()
    if not original.is_absolute():
        raise LocateError("Use an absolute folder path such as /home/you/Games/Conflux.")
    try:
        root = original.resolve(strict=True)
    except (OSError, RuntimeError):
        raise LocateError("The chosen folder does not exist or is not accessible.")
    if not root.is_dir():
        raise LocateError("Please select a directory containing the extracted game.")
    candidates = []
    visited = 0
    truncated = False
    for parent, dirs, files in os.walk(root, topdown=True, followlinks=False):
        visited += 1
        depth = len(Path(parent).relative_to(root).parts)
        if visited > MAX_DIRECTORIES:
            truncated = True
            break
        if depth >= MAX_DEPTH:
            dirs[:] = []
        else:
            dirs[:] = sorted(d for d in dirs if not d.startswith(".")
                             and not (Path(parent) / d).is_symlink())
        if LAUNCHER in files:
            script = Path(parent) / LAUNCHER
            if script.is_file() and not script.is_symlink():
                candidates.append({
                    "path": str(script),
                    "ready": os.access(script, os.X_OK),
                })
                if len(candidates) >= MAX_CANDIDATES:
                    truncated = True
                    break
    return {"directory": str(root), "candidates": candidates, "truncated": truncated}


def valid_launcher(path):
    candidate = Path(path)
    return (candidate.is_absolute() and candidate.name == LAUNCHER
            and candidate.is_file() and not candidate.is_symlink()
            and os.access(candidate, os.X_OK))
