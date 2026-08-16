"""Codex TOML configuration support."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .files import write_config_text

_CODEX_SECTION = re.compile(r"(?m)^\[mcp_servers\.dreamms\]\s*$")
_TOML_SECTION = re.compile(r"(?m)^\[\[?[^\r\n]+\]\]?\s*$")


def render_mcp_block(project_dir: Path) -> str:
    """Render a secret-free Codex MCP block."""

    project_path = json.dumps(project_dir.resolve().as_posix())
    return "\n".join(
        [
            "[mcp_servers.dreamms]",
            'command = "uv"',
            f'args = ["--directory", {project_path}, "run", "dreamms-mcp"]',
            'env_vars = ["DREAM_API_KEY"]',
            "enabled = true",
        ]
    )


def ensure_mcp_block(config_text: str, project_dir: Path) -> str:
    """Insert or replace the DreamMS block without duplicating it."""

    block = render_mcp_block(project_dir)
    match = _CODEX_SECTION.search(config_text)
    if match:
        remainder = config_text[match.end() :]
        next_section = _TOML_SECTION.search(remainder)
        end = match.end() + next_section.start() if next_section else len(config_text)
        prefix = config_text[: match.start()].rstrip("\r\n")
        suffix = config_text[end:].lstrip("\r\n")
        pieces = [part for part in (prefix, block, suffix) if part]
        return "\n\n".join(pieces).rstrip() + "\n"
    existing = config_text.rstrip()
    return f"{existing}\n\n{block}\n" if existing else f"{block}\n"


def write_config(config_path: Path, project_dir: Path) -> bool:
    """Add or update DreamMS in a Codex config."""

    previous = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    updated = ensure_mcp_block(previous, project_dir)
    return write_config_text(config_path, previous, updated)
