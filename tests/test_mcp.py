from __future__ import annotations

import asyncio
import inspect

import pytest


def call(value):
    return asyncio.run(value) if inspect.isawaitable(value) else value


ENDPOINTS = {
    "get_usage",
    "get_economy",
    "get_player",
    "get_rankings",
    "get_expeditions",
    "get_event",
    "get_population",
    "get_changelog",
    "get_account",
    "get_content",
}


def test_all_documented_endpoints_are_registered(server_module):
    tools = call(server_module.mcp.list_tools())
    names = {tool.name for tool in tools}
    assert names == ENDPOINTS


@pytest.mark.parametrize(
    ("function_name", "kwargs", "path", "params"),
    [
        ("get_usage", {}, "/api/v1/usage", {}),
        (
            "get_economy",
            {"item": " White Scroll ", "period": "90"},
            "/api/v1/economy",
            {"item": "White Scroll", "period": "90"},
        ),
        (
            "get_player",
            {"name": "Issue, misaki"},
            "/api/v1/player",
            {"name": "Issue,misaki"},
        ),
        (
            "get_rankings",
            {"type": "job", "job": 412, "page": 2, "limit": 50},
            "/api/v1/rankings",
            {"type": "job", "job": 412, "page": 2, "limit": 50},
        ),
        (
            "get_expeditions",
            {"range": "30d", "type": "fastest"},
            "/api/v1/expeditions",
            {"range": "30d", "type": "fastest"},
        ),
        (
            "get_event",
            {"event": "sgpq2026", "type": "pq"},
            "/api/v1/event",
            {"event": "sgpq2026", "type": "pq"},
        ),
        ("get_population", {}, "/api/v1/population", {}),
        (
            "get_changelog",
            {"count": 3, "format": "text"},
            "/api/v1/changelog",
            {"count": 3, "format": "text"},
        ),
        (
            "get_account",
            {"discord_id": "123456789012345678"},
            "/api/v1/account",
            {"discord_id": "123456789012345678"},
        ),
        (
            "get_content",
            {"discord_id": "123456789012345678"},
            "/api/v1/content",
            {"discord_id": "123456789012345678"},
        ),
    ],
)
def test_tool_parameter_mapping(
    monkeypatch, server_module, function_name, kwargs, path, params
):
    seen = {}

    async def fake_request(request_path, **request_params):
        seen["path"] = request_path
        seen["params"] = request_params
        return {"ok": True, "data": {}}

    monkeypatch.setattr(server_module, "_request", fake_request)
    assert call(getattr(server_module, function_name)(**kwargs)) == {
        "ok": True,
        "data": {},
    }
    assert seen == {"path": path, "params": params}


@pytest.mark.parametrize(
    ("function_name", "kwargs", "message"),
    [
        ("get_economy", {"item": "", "period": "30"}, "item"),
        ("get_economy", {"item": "scroll", "period": "31"}, "period"),
        ("get_player", {"name": ","}, "name"),
        ("get_player", {"name": ",".join(f"p{i}" for i in range(19))}, "18"),
        ("get_rankings", {"type": "job"}, "job"),
        ("get_rankings", {"type": "overall", "page": 0}, "page"),
        ("get_rankings", {"type": "overall", "limit": 51}, "limit"),
        ("get_expeditions", {"range": "1h"}, "range"),
        ("get_event", {"event": "unknown"}, "event"),
        ("get_event", {"event": "sgpq2026", "type": "bad"}, "type"),
        ("get_changelog", {"count": 21}, "count"),
        ("get_account", {"discord_id": "not-numeric"}, "discord_id"),
    ],
)
def test_tool_validation_returns_secret_free_error(
    monkeypatch, server_module, function_name, kwargs, message
):
    async def fail_if_called(*args, **kwargs):
        raise AssertionError("invalid tool input must not call the API")

    monkeypatch.setattr(server_module, "_request", fail_if_called)
    result = call(getattr(server_module, function_name)(**kwargs))
    assert result["error"]["code"] == "invalid_parameter"
    assert message in result["error"]["message"]
