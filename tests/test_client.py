from __future__ import annotations

import httpx
import pytest

from dreamms_mcp.errors import (
    DreamMSAPIError,
    DreamMSHTTPError,
    DreamMSJSONError,
    DreamMSNetworkError,
)

SUCCESS = {"ok": True, "data": {"value": 42}, "meta": {"cachedAt": "now"}}


def test_get_preserves_envelope_and_maps_query(client_factory, request_log, run_async):
    client = client_factory(lambda request: httpx.Response(200, json=SUCCESS))

    result = run_async(
        client.get(
            "/api/v1/rankings",
            params={"type": "job", "job": 412, "page": 2, "limit": 50},
        )
    )

    assert result == SUCCESS
    request = request_log[0]
    assert request.method == "GET"
    assert request.url.path == "/api/v1/rankings"
    assert dict(request.url.params) == {
        "type": "job",
        "job": "412",
        "page": "2",
        "limit": "50",
    }


def test_api_key_uses_recommended_header(client_factory, request_log, run_async):
    client = client_factory(
        lambda request: httpx.Response(200, json=SUCCESS), api_key="secret-key"
    )
    run_async(client.get("/api/v1/usage"))

    request = request_log[0]
    assert request.headers["X-API-Key"] == "secret-key"
    assert "Authorization" not in request.headers
    assert "key" not in request.url.params


def test_successful_error_envelope_raises_api_error(client_factory, run_async):
    client = client_factory(
        lambda request: httpx.Response(
            200,
            json={
                "ok": False,
                "error": {"code": "bad_request", "message": "invalid item"},
            },
        )
    )

    with pytest.raises(DreamMSAPIError, match="invalid item"):
        run_async(client.get("/api/v1/economy"))


@pytest.mark.parametrize("status_code", [400, 401, 404, 405, 429, 503])
def test_documented_http_errors_are_mapped(client_factory, run_async, status_code):
    client = client_factory(
        lambda request: httpx.Response(
            status_code,
            json={"error": {"code": "api_error", "message": "upstream failure"}},
            headers={"Retry-After": "7"},
        )
    )

    with pytest.raises(DreamMSHTTPError) as raised:
        run_async(client.get("/api/v1/usage"))
    assert raised.value.status_code == status_code
    assert raised.value.retry_after == "7"


def test_invalid_success_json_raises_json_error(client_factory, run_async):
    client = client_factory(
        lambda request: httpx.Response(
            200, content=b"not-json", headers={"content-type": "application/json"}
        )
    )

    with pytest.raises(DreamMSJSONError):
        run_async(client.get("/api/v1/usage"))


def test_network_errors_are_safe(client_factory, run_async):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("secret-key unavailable", request=request)

    client = client_factory(handler, api_key="secret-key")
    with pytest.raises(DreamMSNetworkError, match="could not be completed"):
        run_async(client.get("/api/v1/usage"))


def test_api_key_is_redacted_from_upstream_error(client_factory, run_async):
    secret = "secret-key"
    client = client_factory(
        lambda request: httpx.Response(
            401,
            json={"error": {"code": "unauthorized", "message": f"bad key {secret}"}},
        ),
        api_key=secret,
    )

    with pytest.raises(DreamMSHTTPError) as raised:
        run_async(client.get("/api/v1/usage"))
    assert secret not in str(raised.value)
    assert "[redacted]" in str(raised.value)
