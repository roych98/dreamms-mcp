"""OS-level persistence for the DreamMS API key."""

from __future__ import annotations

import os
import re
import shlex
import sys
from pathlib import Path

from .constants import API_KEY_ENV

_START = "# BEGIN dreamms-mcp managed environment"
_END = "# END dreamms-mcp managed environment"


def _windows_user_key() -> str:
    if sys.platform != "win32":
        return ""
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, API_KEY_ENV)
    except (FileNotFoundError, OSError):
        return ""
    return value.strip() if isinstance(value, str) else ""


def current_or_persisted_key() -> str:
    """Return the current key or the wizard's Windows-persisted key."""

    return os.getenv(API_KEY_ENV, "").strip() or _windows_user_key()


def _broadcast_windows_change() -> None:
    if sys.platform != "win32":
        return
    import ctypes

    result = ctypes.c_ulong()
    ctypes.windll.user32.SendMessageTimeoutW(
        0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, ctypes.byref(result)
    )


def _write_unix_key(value: str) -> str:
    shell = Path(os.getenv("SHELL", "")).name
    candidates = [Path.home() / ".zshrc", Path.home() / ".profile"]
    if shell != "zsh":
        candidates = [Path.home() / ".bashrc", Path.home() / ".profile"]
    target = next((path for path in candidates if path.exists()), candidates[-1])
    block = f"{_START}\nexport {API_KEY_ENV}={shlex.quote(value)}\n{_END}\n"
    previous = target.read_text(encoding="utf-8") if target.exists() else ""
    pattern = re.compile(rf"{re.escape(_START)}.*?{re.escape(_END)}\n?", re.DOTALL)
    updated = pattern.sub(block, previous)
    if updated == previous:
        updated = previous.rstrip() + "\n\n" + block
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(updated, encoding="utf-8")
    try:
        target.chmod(0o600)
    except OSError:
        pass
    return str(target)


def persist_key(api_key: str) -> str:
    """Persist a key and make it available to the wizard process."""

    value = api_key.strip()
    if not value:
        raise ValueError("API key cannot be empty")
    os.environ[API_KEY_ENV] = value
    if sys.platform == "win32":
        import winreg

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            winreg.SetValueEx(key, API_KEY_ENV, 0, winreg.REG_SZ, value)
        _broadcast_windows_change()
        return "Windows user environment"
    return _write_unix_key(value)
