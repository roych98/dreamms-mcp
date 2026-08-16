"""Runtime validators for the parameter constraints in the DreamMS docs."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import TypeVar

from .errors import DreamMSError

T = TypeVar("T")


def required_text(value: str, name: str) -> str:
    """Require a non-empty string and normalize surrounding whitespace."""

    if not isinstance(value, str) or not value.strip():
        raise DreamMSError(
            f"{name} must be a non-empty string.", code="invalid_parameter"
        )
    return value.strip()


def choice(value: T, allowed: Iterable[T], name: str) -> T:
    """Require a value from a documented finite set."""

    allowed_values = tuple(allowed)
    if value not in allowed_values:
        formatted = ", ".join(repr(item) for item in allowed_values)
        raise DreamMSError(
            f"{name} must be one of: {formatted}.", code="invalid_parameter"
        )
    return value


def bounded_int(
    value: int, name: str, *, minimum: int, maximum: int | None = None
) -> int:
    """Require an integer in an inclusive documented range."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise DreamMSError(f"{name} must be an integer.", code="invalid_parameter")
    if value < minimum or (maximum is not None and value > maximum):
        bound = (
            f"at least {minimum}"
            if maximum is None
            else f"between {minimum} and {maximum}"
        )
        raise DreamMSError(f"{name} must be {bound}.", code="invalid_parameter")
    return value


def player_names(value: str) -> str:
    """Validate the comma-separated player search limit of eighteen names."""

    value = required_text(value, "name")
    names = [name.strip() for name in value.split(",")]
    if any(not name for name in names):
        raise DreamMSError(
            "name must contain only non-empty comma-separated names.",
            code="invalid_parameter",
        )
    if len(names) > 18:
        raise DreamMSError(
            "name may contain at most 18 comma-separated names.",
            code="invalid_parameter",
        )
    return ",".join(names)


def discord_id(value: str) -> str:
    """Validate the numeric Discord user identifier accepted by app endpoints."""

    value = required_text(value, "discord_id")
    if not re.fullmatch(r"\d{1,20}", value):
        raise DreamMSError(
            "discord_id must be a numeric Discord user id.", code="invalid_parameter"
        )
    return value
