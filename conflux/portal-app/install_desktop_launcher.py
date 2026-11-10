"""Install a local-only Conflux Portal desktop launcher for the current user."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def escape_exec_arg(value):
    # XDG Desktop Entry quoting: escape backslash, quote, dollar and backtick.
    if "%" in value or "\n" in value or "\r" in value:
        raise ValueError("Desktop file paths cannot contain percent signs or newlines.")
    value = value.replace("\\", "\\\\").replace('"', '\\"')
    value = value.replace("$", "\\$").replace("`", "\\`")
    return '"' + value + '"'


def install_desktop_launcher():
    data_home = Path(os.environ.get(
        "XDG_DATA_HOME", str(Path.home() / ".local" / "share"))).expanduser()
    if not data_home.is_absolute():
        raise ValueError("XDG_DATA_HOME must be an absolute path.")
    destination = data_home / "applications" / "conflux-portal.desktop"
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = " ".join([
        escape_exec_arg(sys.executable),
        escape_exec_arg(str(ROOT / "portal_desktop.py")),
    ])
    content = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Conflux Portal\n"
        "Comment=Your local entrance to Conflux\n"
        "Categories=Game;Utility;\n"
        "Icon=applications-games\n"
        "Terminal=false\n"
        "StartupNotify=true\n"
        "Exec=" + command + "\n"
    )
    # Do not replace an arbitrary third-party symlink.
    if destination.is_symlink():
        raise OSError("Refusing to replace a linked desktop entry.")
    destination.write_text(content, encoding="utf-8")
    destination.chmod(0o644)
    return str(destination)


if __name__ == "__main__":
    print("Installed:", install_desktop_launcher())
