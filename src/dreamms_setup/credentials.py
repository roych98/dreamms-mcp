"""OS-level persistence for DreamMS setup values."""

from __future__ import annotations

import os
import re
import shlex
import sys
from pathlib import Path

from .constants import API_KEY_ENV, DISCORD_ID_ENV

_START = "# BEGIN dreamms-mcp managed environment"
_END = "# END dreamms-mcp managed environment"


def _windows_user_value(name: str) -> str:
    if sys.platform != "win32":
        return ""
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
    except (FileNotFoundError, OSError):
        return ""
    return value.strip() if isinstance(value, str) else ""


def current_or_persisted_key() -> str:
    """Return the current key or the wizard's Windows-persisted key."""

    return os.getenv(API_KEY_ENV, "").strip() or _windows_user_value(API_KEY_ENV)


def current_or_persisted_discord_id() -> str:
    """Return the current or Windows-persisted Discord user ID."""

    return os.getenv(DISCORD_ID_ENV, "").strip() or _windows_user_value(DISCORD_ID_ENV)


def _broadcast_windows_change() -> None:
    if sys.platform != "win32":
        return
    import ctypes

    result = ctypes.c_ulong()
    ctypes.windll.user32.SendMessageTimeoutW(
        0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, ctypes.byref(result)
    )


def _write_unix_value(name: str, value: str) -> str:
    shell = Path(os.getenv("SHELL", "")).name
    candidates = [Path.home() / ".zshrc", Path.home() / ".profile"]
    if shell != "zsh":
        candidates = [Path.home() / ".bashrc", Path.home() / ".profile"]
    target = next((path for path in candidates if path.exists()), candidates[-1])
    previous = target.read_text(encoding="utf-8") if target.exists() else ""
    pattern = re.compile(rf"{re.escape(_START)}.*?{re.escape(_END)}\n?", re.DOTALL)
    line = f"export {name}={shlex.quote(value)}"
    match = pattern.search(previous)
    if match:
        block = match.group(0)
        assignment = re.compile(rf"(?m)^export {re.escape(name)}=.*$")
        if assignment.search(block):
            block = assignment.sub(line, block)
        else:
            block = block.replace(_END, f"{line}\n{_END}")
        updated = previous[: match.start()] + block + previous[match.end() :]
    else:
        block = f"{_START}\n{line}\n{_END}\n"
        updated = previous.rstrip() + "\n\n" + block
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(updated, encoding="utf-8")
    try:
        target.chmod(0o600)
    except OSError:
        pass
    return str(target)


def _persist_value(name: str, value: str) -> str:
    """Persist a setup value and make it available to this process."""

    value = value.strip()
    if not value:
        raise ValueError("Setup value cannot be empty")
    os.environ[name] = value
    if sys.platform == "win32":
        import winreg

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        _broadcast_windows_change()
        return "Windows user environment"
    return _write_unix_value(name, value)


def persist_key(api_key: str) -> str:
    """Persist an API key and make it available to the wizard process."""

    return _persist_value(API_KEY_ENV, api_key)


def persist_discord_id(discord_id: str) -> str:
    """Persist a Discord user ID for app-authenticated endpoints."""

    return _persist_value(DISCORD_ID_ENV, discord_id)
