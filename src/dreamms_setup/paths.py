"""Client and scope-specific configuration paths."""

from __future__ import annotations

import os
from pathlib import Path

from .constants import CLIENT_LABELS, SUPPORTED_SCOPES


def client_label(client: str) -> str:
    """Return a display name for a supported coding agent."""

    try:
        return CLIENT_LABELS[client]
    except KeyError as exc:
        raise ValueError(f"Unsupported client: {client}") from exc


def client_config_path(
    client: str,
    home: Path | None = None,
    *,
    scope: str = "user",
    project_dir: Path | None = None,
) -> Path:
    """Return the native config path for a client and scope."""

    if scope not in SUPPORTED_SCOPES:
        raise ValueError(f"Unsupported scope: {scope}")
    home = home or Path.home()
    if scope == "project":
        project = (project_dir or Path.cwd()).resolve()
        paths = {
            "codex": project / ".codex" / "config.toml",
            "claude": project / ".mcp.json",
            "opencode": project / "opencode.json",
            "pi": project / ".mcp.json",
        }
    else:
        paths = {
            "codex": home / ".codex" / "config.toml",
            "claude": home / ".claude.json",
            "opencode": home / ".config" / "opencode" / "opencode.json",
            "pi": home / ".pi" / "agent" / "mcp.json",
        }
    try:
        path = paths[client]
    except KeyError as exc:
        raise ValueError(f"Unsupported client: {client}") from exc
    if client == "opencode" and scope == "user":
        custom_path = os.getenv("OPENCODE_CONFIG", "").strip()
        if custom_path:
            return Path(custom_path).expanduser()
        jsonc_path = path.with_suffix(".jsonc")
        if jsonc_path.exists() and not path.exists():
            return jsonc_path
    return path
