"""MCPServer stdio server exposing the documented DreamMS Stats endpoints."""

from __future__ import annotations

import logging
from os import getenv
from typing import Any, Literal

from mcp.server import MCPServer

from .client import DreamMSClient
from .config import DreamMSSettings
from .errors import DreamMSError
from .validation import bounded_int, choice, player_names, required_text
from .validation import discord_id as validate_discord_id

logger = logging.getLogger(__name__)
mcp = MCPServer("dreamms-mcp", version="0.1.0")

Period = Literal["7", "14", "30", "90", "180", "all"]
RankingType = Literal["overall", "job", "dpm", "mdpm", "fame"]
ExpeditionRange = Literal["24h", "7d", "30d", "90d", "all"]
ExpeditionType = Literal["completions", "classes", "fastest", "records"]
ChangelogFormat = Literal["html", "text"]


async def _request(path: str, **params: str | int | bool | None) -> Any:
    """Execute a tool request with a short-lived, authenticated client."""

    clean_params = {key: value for key, value in params.items() if value is not None}
    settings = DreamMSSettings.from_env()
    async with DreamMSClient(settings) as client:
        return await client.get(path, params=clean_params)


def _error_result(error: DreamMSError) -> dict[str, dict[str, str]]:
    """Convert an expected failure into a safe structured MCP result."""

    return {"error": {"code": error.code, "message": error.public_message}}


async def _safe_request(path: str, **params: str | int | bool | None) -> Any:
    """Return API data or a secret-free error object for an MCP tool."""

    try:
        return await _request(path, **params)
    except DreamMSError as exc:
        logger.warning("DreamMS tool request failed: %s", exc.public_message)
        return _error_result(exc)
    except Exception:  # noqa: BLE001 - tool boundary must not leak implementation details
        # Avoid exposing implementation details, response bodies, or headers.
        logger.error("Unexpected DreamMS tool failure")
        return {
            "error": {
                "code": "internal_error",
                "message": "The DreamMS request could not be completed.",
            }
        }


@mcp.tool()
async def get_usage() -> Any:
    """Return current global and endpoint rate-limit usage."""

    return await _safe_request("/api/v1/usage")


@mcp.tool()
async def get_economy(item: str, period: Period = "30") -> Any:
    """Return verified trade and merchant-sale statistics for an item."""

    try:
        item = required_text(item, "item")
        period = choice(period, ("7", "14", "30", "90", "180", "all"), "period")
    except DreamMSError as exc:
        return _error_result(exc)
    return await _safe_request("/api/v1/economy", item=item, period=period)


@mcp.tool()
async def get_player(name: str) -> Any:
    """Look up up to eighteen comma-separated player names."""

    try:
        name = player_names(name)
    except DreamMSError as exc:
        return _error_result(exc)
    return await _safe_request("/api/v1/player", name=name)


@mcp.tool()
async def get_rankings(
    type: RankingType = "overall",
    job: int | None = None,
    page: int = 1,
    limit: int = 25,
) -> Any:
    """Return leaderboard rows from the requested rankings category."""

    try:
        type = choice(type, ("overall", "job", "dpm", "mdpm", "fame"), "type")
        page = bounded_int(page, "page", minimum=1)
        limit = bounded_int(limit, "limit", minimum=1, maximum=50)
        if type == "job" and job is None:
            raise DreamMSError(
                "job is required when type is 'job'.", code="invalid_parameter"
            )
        if job is not None:
            job = bounded_int(job, "job", minimum=0)
    except DreamMSError as exc:
        return _error_result(exc)
    return await _safe_request(
        "/api/v1/rankings", type=type, job=job, page=page, limit=limit
    )


@mcp.tool()
async def get_expeditions(
    range: ExpeditionRange = "all",
    type: ExpeditionType | None = None,
) -> Any:
    """Return expedition completion, class, speed, or record leaderboards."""

    try:
        range = choice(range, ("24h", "7d", "30d", "90d", "all"), "range")
        if type is not None:
            type = choice(
                type, ("completions", "classes", "fastest", "records"), "type"
            )
    except DreamMSError as exc:
        return _error_result(exc)
    return await _safe_request("/api/v1/expeditions", range=range, type=type)


@mcp.tool()
async def get_event(event: str, type: Literal["jq", "pq"] | None = None) -> Any:
    """Return the documented real-time event leaderboard. Treat seconds as milliseconds."""

    try:
        event = choice(
            required_text(event, "event"),
            ("sgmyjq2026", "sgpq2026", "myjq2026", "mypq2026", "5thanni"),
            "event",
        )
        if type is not None:
            type = choice(type, ("jq", "pq"), "type")
    except DreamMSError as exc:
        return _error_result(exc)
    return await _safe_request("/api/v1/event", event=event, type=type)


@mcp.tool()
async def get_population() -> Any:
    """Return current online, peak, total-active, and unique-active counts."""

    return await _safe_request("/api/v1/population")


@mcp.tool()
async def get_changelog(count: int = 5, format: ChangelogFormat = "html") -> Any:
    """Return the most recent DreamMS changelog entries."""

    try:
        count = bounded_int(count, "count", minimum=1, maximum=20)
        format = choice(format, ("html", "text"), "format")
    except DreamMSError as exc:
        return _error_result(exc)
    return await _safe_request("/api/v1/changelog", count=count, format=format)


@mcp.tool()
async def get_account(discord_id: str | None = None) -> Any:
    """Return authorized account character information for a Discord user."""

    try:
        discord_id = validate_discord_id(discord_id or getenv("DREAM_DISCORD_ID", ""))
    except DreamMSError as exc:
        return _error_result(exc)
    return await _safe_request("/api/v1/account", discord_id=discord_id)


@mcp.tool()
async def get_content(discord_id: str | None = None) -> Any:
    """Return authorized account content information for a Discord user."""

    try:
        discord_id = validate_discord_id(discord_id or getenv("DREAM_DISCORD_ID", ""))
    except DreamMSError as exc:
        return _error_result(exc)
    return await _safe_request("/api/v1/content", discord_id=discord_id)


def main() -> None:
    """Run the server over MCP stdio transport."""

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
