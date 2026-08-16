from __future__ import annotations

import json
from pathlib import Path

from dreamms_setup import codex_config, json_config
from dreamms_setup.paths import client_config_path


def test_render_codex_block_uses_secret_free_env_reference(tmp_path: Path):
    block = codex_config.render_mcp_block(tmp_path)

    assert "mcp_servers.dreamms" in block
    assert "DREAM_API_KEY" in block
    assert "api-key" not in block
    assert str(tmp_path).replace("\\", "/") in block


def test_insert_codex_block_preserves_existing_config(tmp_path: Path):
    updated = codex_config.ensure_mcp_block('model = "gpt-5"\n', tmp_path)

    assert 'model = "gpt-5"' in updated
    assert updated.count("[mcp_servers.dreamms]") == 1


def test_replace_existing_codex_block_without_duplication(tmp_path: Path):
    original = """[mcp_servers.dreamms]
command = \"old\"

[mcp_servers.other]
enabled = true
"""

    updated = codex_config.ensure_mcp_block(original, tmp_path)

    assert updated.count("[mcp_servers.dreamms]") == 1
    assert 'command = "old"' not in updated
    assert "[mcp_servers.other]" in updated


def test_write_codex_config_is_idempotent(tmp_path: Path):
    config_path = tmp_path / ".codex" / "config.toml"
    config_path.parent.mkdir()
    config_path.write_text('model = "gpt-5"\n', encoding="utf-8")

    assert codex_config.write_config(config_path, tmp_path) is True
    first = config_path.read_text(encoding="utf-8")
    assert codex_config.write_config(config_path, tmp_path) is False
    assert config_path.read_text(encoding="utf-8") == first
    assert config_path.with_suffix(".toml.dreamms-backup").exists()


def test_client_config_paths_are_user_scoped(tmp_path: Path):
    assert client_config_path("claude", tmp_path) == tmp_path / ".claude.json"
    assert client_config_path("opencode", tmp_path) == (
        tmp_path / ".config" / "opencode" / "opencode.json"
    )
    assert client_config_path("pi", tmp_path) == tmp_path / ".pi" / "agent" / "mcp.json"


def test_client_config_paths_are_project_scoped(tmp_path: Path):
    assert client_config_path("codex", scope="project", project_dir=tmp_path) == (
        tmp_path / ".codex" / "config.toml"
    )
    assert client_config_path("claude", scope="project", project_dir=tmp_path) == (
        tmp_path / ".mcp.json"
    )
    assert client_config_path("opencode", scope="project", project_dir=tmp_path) == (
        tmp_path / "opencode.json"
    )
    assert client_config_path("pi", scope="project", project_dir=tmp_path) == (
        tmp_path / ".mcp.json"
    )


def test_render_json_servers_use_environment_references(tmp_path: Path):
    claude = json_config.render_server("claude", tmp_path)
    opencode = json_config.render_server("opencode", tmp_path)
    pi = json_config.render_server("pi", tmp_path)

    assert claude["env"] == {"DREAM_API_KEY": "${DREAM_API_KEY}"}
    assert opencode["environment"] == {"DREAM_API_KEY": "{env:DREAM_API_KEY}"}
    assert pi["env"] == {"DREAM_API_KEY": "${DREAM_API_KEY}"}
    assert "secret" not in json.dumps([claude, opencode, pi])


def test_write_json_client_configs_preserves_other_servers(tmp_path: Path):
    config_path = tmp_path / "opencode.json"
    config_path.write_text(
        json.dumps({"model": "test", "mcp": {"servers": {"other": {}}}}),
        encoding="utf-8",
    )

    assert json_config.write_config(config_path, "opencode", tmp_path) is True
    data = json.loads(config_path.read_text(encoding="utf-8"))

    assert data["model"] == "test"
    assert set(data["mcp"]["servers"]) == {"other", "dreamms"}
    assert data["mcp"]["servers"]["dreamms"]["type"] == "local"
    assert config_path.with_suffix(".json.dreamms-backup").exists()


def test_write_opencode_jsonc_config(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "opencode.jsonc"
    config_path.write_text(
        """{
          // Keep the existing model.
          \"model\": \"test\",
          \"mcp\": {\"servers\": {},},
        }
        """,
        encoding="utf-8",
    )
    monkeypatch.setenv("OPENCODE_CONFIG", str(config_path))

    assert json_config.write_config(config_path, "opencode", tmp_path) is True
    data = json.loads(config_path.read_text(encoding="utf-8"))

    assert data["model"] == "test"
    assert data["mcp"]["servers"]["dreamms"]["environment"] == {
        "DREAM_API_KEY": "{env:DREAM_API_KEY}"
    }
