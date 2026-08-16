"""Public, secret-free exceptions raised by the DreamMS integration."""

from __future__ import annotations


class DreamMSError(Exception):
    """Base class for expected DreamMS client and API failures."""

    code = "dreamms_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code

    @property
    def public_message(self) -> str:
        """Return the safe message intended for an MCP consumer."""

        return self.message


class DreamMSConfigurationError(DreamMSError):
    """Raised when the server cannot build a valid API configuration."""

    code = "configuration_error"


class DreamMSNetworkError(DreamMSError):
    """Raised when a request cannot reach DreamMS or times out."""

    code = "network_error"


class DreamMSJSONError(DreamMSError):
    """Raised when DreamMS returns a successful response that is not JSON."""

    code = "invalid_json"


class DreamMSHTTPError(DreamMSError):
    """Raised for an HTTP response with a non-success status code."""

    code = "http_error"

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        api_code: str | None = None,
        retry_after: str | None = None,
    ) -> None:
        super().__init__(message, code=api_code or self.code)
        self.status_code = status_code
        self.api_code = api_code
        self.retry_after = retry_after


class DreamMSAPIError(DreamMSError):
    """Raised when DreamMS returns a JSON API error envelope."""

    code = "api_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message, code=code or self.code)
