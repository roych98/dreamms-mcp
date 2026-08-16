"""Environment-backed configuration for the DreamMS API client."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse

from .errors import DreamMSConfigurationError

DEFAULT_API_BASE_URL = "https://dreamms.gg"


@dataclass(frozen=True, slots=True)
class DreamMSSettings:
    """Validated settings used for every DreamMS request.

    The API key is intentionally kept out of the representation and is never
    included in an exception, log message, or tool result.
    """

    api_key: str
    base_url: str = DEFAULT_API_BASE_URL
    timeout_seconds: float = 30.0

    def __repr__(self) -> str:
        """Avoid accidentally exposing the credential in diagnostics."""

        return (
            "DreamMSSettings(api_key='<redacted>', "
            f"base_url={self.base_url!r}, timeout_seconds={self.timeout_seconds!r})"
        )

    @classmethod
    def from_env(cls) -> DreamMSSettings:
        """Create settings from ``DREAM_API_KEY`` and optional base URL."""

        api_key = os.getenv("DREAM_API_KEY", "").strip()
        if not api_key:
            raise DreamMSConfigurationError(
                "DREAM_API_KEY is not set; configure it before calling DreamMS."
            )

        base_url = os.getenv("DREAM_API_BASE_URL", DEFAULT_API_BASE_URL).strip()
        if not base_url:
            base_url = DEFAULT_API_BASE_URL
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise DreamMSConfigurationError(
                "DREAM_API_BASE_URL must be an absolute http(s) URL."
            )
        if parsed.query or parsed.fragment:
            raise DreamMSConfigurationError(
                "DREAM_API_BASE_URL must not include a query string or fragment."
            )

        return cls(api_key=api_key, base_url=base_url.rstrip("/"))
