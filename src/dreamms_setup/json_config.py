"""JSON and JSONC configuration support for non-Codex clients."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import API_KEY_ENV
from .files import write_config_text


def render_server(client: str, project_dir: Path) -> dict[str, Any]:
    """Render a native JSON MCP server definition."""

    path = project_dir.resolve().as_posix()
    command = ["uv", "--directory", path, "run", "dreamms-mcp"]
    if client == "claude":
        return {
            "type": "stdio",
            "command": "uv",
            "args": command[1:],
            "env": {API_KEY_ENV: "${DREAM_API_KEY}"},
        }
    if client == "opencode":
        return {
            "type": "local",
            "command": command,
            "environment": {API_KEY_ENV: "{env:DREAM_API_KEY}"},
        }
    if client == "pi":
        return {
            "command": "uv",
            "args": command[1:],
            "env": {API_KEY_ENV: "${DREAM_API_KEY}"},
        }
    raise ValueError(f"Unsupported JSON client: {client}")


def _server_map(data: dict[str, Any], client: str) -> dict[str, Any]:
    if client == "opencode":
        mcp = data.setdefault("mcp", {})
        if not isinstance(mcp, dict):
            raise TypeError("OpenCode config has a non-object 'mcp' value")
        servers = mcp.setdefault("servers", {})
    else:
        servers = data.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise TypeError("MCP server config must be a JSON object")
    return servers


def _strip_comments(text: str) -> str:
    """Remove JSONC comments without changing strings."""

    output: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if in_string:
            output.append(char)
            escaped = char == "\\" and not escaped
            if char == '"' and not escaped:
                in_string = False
            index += 1
        elif char == '"':
            in_string = True
            output.append(char)
            index += 1
        elif char == "/" and next_char == "/":
            index += 2
            while index < len(text) and text[index] not in "\r\n":
                index += 1
        elif char == "/" and next_char == "*":
            index += 2
            while index < len(text):
                if text[index : index + 2] == "*/":
                    index += 2
                    break
                if text[index] in "\r\n":
                    output.append(text[index])
                index += 1
        else:
            output.append(char)
            index += 1
    return "".join(output)


def _strip_trailing_commas(text: str) -> str:
    """Remove JSONC trailing commas outside strings."""

    output: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        char = text[index]
        if in_string:
            output.append(char)
            escaped = char == "\\" and not escaped
            if char == '"' and not escaped:
                in_string = False
            index += 1
        elif char == '"':
            in_string = True
            output.append(char)
            index += 1
        elif char == ",":
            lookahead = index + 1
            while lookahead < len(text) and text[lookahead].isspace():
                lookahead += 1
            if lookahead < len(text) and text[lookahead] in "}]":
                index += 1
            else:
                output.append(char)
                index += 1
        else:
            output.append(char)
            index += 1
    return "".join(output)


def _parse(text: str) -> Any:
    return json.loads(_strip_trailing_commas(_strip_comments(text)))


def write_config(config_path: Path, client: str, project_dir: Path) -> bool:
    """Add or update DreamMS in a Claude, OpenCode, or Pi config."""

    if client not in {"claude", "opencode", "pi"}:
        raise ValueError(f"Unsupported JSON client: {client}")
    previous = config_path.read_text(encoding="utf-8") if config_path.exists() else "{}\n"
    try:
        data = _parse(previous)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{config_path} is not valid JSON/JSONC") from exc
    if not isinstance(data, dict):
        raise TypeError(f"{config_path} must contain a JSON object")
    _server_map(data, client)["dreamms"] = render_server(client, project_dir)
    updated = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return write_config_text(config_path, previous, updated)
