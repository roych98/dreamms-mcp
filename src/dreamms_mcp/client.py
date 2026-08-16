"""Small asynchronous HTTP client for the DreamMS Stats API."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self

import httpx

from .config import DreamMSSettings
from .errors import (
    DreamMSAPIError,
    DreamMSHTTPError,
    DreamMSJSONError,
    DreamMSNetworkError,
)

QueryValue = str | int | bool


def _safe_text(value: Any, *, fallback: str, secret: str = "") -> str:
    """Convert an API error field to short, non-sensitive text."""

    if isinstance(value, str):
        text = " ".join(value.split())
    else:
        text = ""
    if not text:
        return fallback
    # The API key must not escape through a server-provided error message.
    if secret:
        text = text.replace(secret, "[redacted]")
    return text[:300]


class DreamMSClient:
    """Authenticated async client that only exposes JSON GET requests."""

    def __init__(
        self,
        settings: DreamMSSettings,
        *,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings
        self._http = http_client
        self._owns_http = http_client is None

    async def __aenter__(self) -> Self:
        if self._http is None:
            self._http = httpx.AsyncClient(
                base_url=self.settings.base_url,
                timeout=self.settings.timeout_seconds,
                headers={"Accept": "application/json"},
            )
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._owns_http and self._http is not None:
            await self._http.aclose()
            self._http = None

    async def get(
        self,
        path: str,
        *,
        params: Mapping[str, QueryValue] | None = None,
    ) -> Any:
        """GET a documented endpoint and return its decoded JSON payload."""

        if self._http is None:
            raise RuntimeError(
                "DreamMSClient must be used as an async context manager."
            )

        request_path = "/" + path.lstrip("/")
        # Set the credential per request as well as on the client. This keeps
        # authentication reliable with injected transports used by tests.
        headers = {"X-API-Key": self.settings.api_key}
        try:
            response = await self._http.get(
                request_path, params=params, headers=headers
            )
        except httpx.TimeoutException as exc:
            raise DreamMSNetworkError("DreamMS request timed out.") from exc
        except httpx.RequestError as exc:
            raise DreamMSNetworkError(
                "DreamMS request could not be completed."
            ) from exc

        payload: Any | None = None
        try:
            payload = response.json()
        except ValueError as exc:
            if response.is_error:
                raise DreamMSHTTPError(
                    _http_error_message(response.status_code),
                    status_code=response.status_code,
                    retry_after=response.headers.get("Retry-After"),
                ) from exc
            raise DreamMSJSONError("DreamMS returned invalid JSON.") from exc

        if response.is_error:
            raise self._http_error(response, payload, secret=self.settings.api_key)
        if isinstance(payload, Mapping) and payload.get("ok") is False:
            raise self._api_error(payload, secret=self.settings.api_key)
        return payload

    @staticmethod
    def _http_error(
        response: httpx.Response,
        payload: Any,
        *,
        secret: str = "",
    ) -> DreamMSHTTPError:
        """Build a safe HTTP error from the documented or fallback envelope."""

        api_code: str | None = None
        message = _http_error_message(response.status_code)
        if isinstance(payload, Mapping):
            error = payload.get("error")
            if isinstance(error, Mapping):
                candidate_code = error.get("code")
                if isinstance(candidate_code, str) and candidate_code:
                    api_code = candidate_code[:80]
                message = _safe_text(
                    error.get("message"), fallback=message, secret=secret
                )
            elif isinstance(error, str):
                message = _safe_text(error, fallback=message, secret=secret)
        return DreamMSHTTPError(
            message,
            status_code=response.status_code,
            api_code=api_code,
            retry_after=response.headers.get("Retry-After"),
        )

    @staticmethod
    def _api_error(payload: Mapping[str, Any], *, secret: str = "") -> DreamMSAPIError:
        """Build a safe error from a successful HTTP response with ``ok=false``."""

        error = payload.get("error")
        if isinstance(error, Mapping):
            code = error.get("code")
            api_code = code[:80] if isinstance(code, str) and code else None
            message = _safe_text(
                error.get("message"),
                fallback="DreamMS rejected the request.",
                secret=secret,
            )
            return DreamMSAPIError(message, code=api_code)
        return DreamMSAPIError("DreamMS rejected the request.")


def _http_error_message(status_code: int) -> str:
    """Map common status codes to useful messages without echoing response data."""

    messages = {
        400: "DreamMS rejected the request parameters.",
        401: "DreamMS authentication failed.",
        404: "DreamMS could not find a matching record.",
        405: "DreamMS does not allow this HTTP method.",
        429: "DreamMS rate limit exceeded; try again later.",
        503: "DreamMS is temporarily unavailable.",
    }
    return messages.get(status_code, f"DreamMS returned HTTP {status_code}.")
