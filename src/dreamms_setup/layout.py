"""Textual widget layout for the DreamMS setup wizard."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal
from textual.widgets import Button, Input, Label, Select, Static

from .constants import (
    CLIENT_LABELS,
    CLIENT_NOTES,
    SCOPE_LABELS,
    SUPPORTED_CLIENTS,
    SUPPORTED_SCOPES,
)


def compose_body(wizard: Any) -> ComposeResult:
    """Build the centered setup panel and its responsive form."""

    with Horizontal(id="title-row"):
        with Container(id="title-copy"):
            yield Static("DreamMS MCP Setup", id="title")
            yield Static(
                "Configure the local server for your coding agent", id="subtitle"
            )
        yield Static("LOCAL ONLY", id="badge")
    yield Static(
        "[bold #67b3ff]i[/]  This wizard configures the local DreamMS MCP for your coding agent.\n"
        "     Your API key is saved to your user environment, never to client config files.",
        id="intro",
    )
    with Grid(id="form-grid"):
        with Container(classes="field-group"):
            yield Label("Dream MS API key", classes="field-label")
            yield Input(
                placeholder="Paste your key, or leave blank to keep the existing key",
                password=True,
                id="api-key",
            )
            yield Static(wizard._key_status(), id="hint", classes="field-hint")
            yield Label("Discord ID (optional)", classes="field-label")
            yield Input(
                placeholder="Your numeric Discord user ID for app APIs",
                id="discord-id",
            )
            yield Static(
                wizard._discord_id_status(), id="discord-hint", classes="field-hint"
            )
        with Container(classes="field-group"):
            yield Label("Coding agent", classes="field-label")
            yield Select(
                [(CLIENT_LABELS[client], client) for client in SUPPORTED_CLIENTS],
                value="codex",
                id="client",
            )
            yield Static(CLIENT_NOTES["codex"], id="client-note", classes="field-hint")
            yield Label("Scope", classes="field-label")
            yield Select(
                [(SCOPE_LABELS[scope], scope) for scope in SUPPORTED_SCOPES],
                value="user",
                id="scope",
            )
    with Horizontal(id="buttons"):
        yield Button("Configure MCP", variant="primary", id="configure")
        yield Button("Test connection", id="test")
        yield Button("Quit", id="quit")
    with Grid(id="details"):
        yield Static("Ready.", id="status")
        with Container(id="config-card"):
            yield Label("Codex configuration", classes="field-label", id="client-label")
            yield Static(str(wizard._initial_path()), id="config-path")
            yield Static(CLIENT_NOTES["codex"], id="detail-note")
