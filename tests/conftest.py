from __future__ import annotations

import asyncio
import sys
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dreamms_mcp.client import DreamMSClient
from dreamms_mcp.config import DreamMSSettings


@pytest.fixture
def request_log() -> list[httpx.Request]:
    return []


@pytest.fixture
def client_factory(request_log: list[httpx.Request]):
    clients: list[DreamMSClient] = []

    def factory(
        handler: Callable[[httpx.Request], httpx.Response] | None = None,
        *,
        api_key: str = "test-key",
    ) -> DreamMSClient:
        def wrapped(request: httpx.Request) -> httpx.Response:
            request_log.append(request)
            if handler is None:
                return httpx.Response(200, json={"ok": True, "data": {}})
            return handler(request)

        http_client = httpx.AsyncClient(
            base_url="https://dreamms.test",
            transport=httpx.MockTransport(wrapped),
        )
        client = DreamMSClient(
            DreamMSSettings(api_key=api_key, base_url="https://dreamms.test"),
            http_client=http_client,
        )
        clients.append(client)
        return client

    yield factory
    for client in clients:
        asyncio.run(client.__aexit__(None, None, None))


@pytest.fixture
def run_async():
    return asyncio.run


@pytest.fixture
def server_module():
    from dreamms_mcp import server

    return server
