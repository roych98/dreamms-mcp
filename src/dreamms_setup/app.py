"""Textual application for configuring DreamMS MCP clients."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

from dreamms_mcp.client import DreamMSClient
from dreamms_mcp.config import DreamMSSettings
from dreamms_mcp.errors import DreamMSError

from .codex_config import write_config as write_codex_config
from .constants import (
    API_KEY_ENV,
    CLIENT_LABELS,
    CLIENT_NOTES,
    SCOPE_LABELS,
    SUPPORTED_CLIENTS,
    SUPPORTED_SCOPES,
)
from .credentials import current_or_persisted_key, persist_key
from .json_config import write_config as write_json_config
from .paths import client_config_path, client_label
from .styles import CSS


class SetupWizard(App[None]):
    """Interactive, local-only setup flow for MCP coding agents."""

    TITLE = "DreamMS MCP Setup"
    SUB_TITLE = "Configure the local server for your coding agent"
    CSS = CSS
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("ctrl+q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="app"):
            yield Static(
                "This wizard configures the local DreamMS MCP for your coding agent. "
                "Your API key is saved to your user environment and never to "
                "client configuration files.",
                id="intro",
            )
            yield Label("Dream MS API key", classes="field-label")
            yield Input(
                placeholder="Paste your key, or leave blank to keep the existing key",
                password=True,
                id="api-key",
            )
            yield Static(self._key_status(), id="hint")
            yield Label("Coding agent", classes="field-label")
            yield Select(
                [(CLIENT_LABELS[client], client) for client in SUPPORTED_CLIENTS],
                value="codex",
                id="client",
            )
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
            yield Label("Codex configuration", classes="field-label", id="client-label")
            yield Static(str(self._initial_path()), id="config-path")
            yield Static(CLIENT_NOTES["codex"], id="client-note")
            yield Static("Ready.", id="status")
        yield Footer()

    def _initial_path(self) -> Path:
        return client_config_path("codex", scope="user", project_dir=Path.cwd())

    def _key_status(self) -> str:
        if current_or_persisted_key():
            return f"{API_KEY_ENV} detected. Leave the field blank to reuse it."
        return f"{API_KEY_ENV} is not set yet."

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.exit()
        elif event.button.id == "configure":
            self._configure()
        elif event.button.id == "test":
            self.run_worker(self._test_connection, exclusive=True)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value is Select.BLANK:
            return
        if event.select.id == "client":
            client = str(event.value)
            self.query_one("#client-label", Label).update(
                f"{client_label(client)} configuration"
            )
            self.query_one("#client-note", Static).update(CLIENT_NOTES[client])
        elif event.select.id != "scope":
            return
        self.query_one("#config-path", Static).update(str(self._selected_path()))

    def _selected_path(self) -> Path:
        client = str(self.query_one("#client", Select).value)
        scope = str(self.query_one("#scope", Select).value)
        return client_config_path(client, scope=scope, project_dir=Path.cwd())

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def _configure(self) -> None:
        entered = self.query_one("#api-key", Input).value.strip()
        api_key = entered or current_or_persisted_key()
        if not api_key:
            self._set_status("[bold red]No API key provided.[/] Paste your key first.")
            return
        try:
            storage = persist_key(api_key) if entered else "existing environment"
            client = str(self.query_one("#client", Select).value)
            scope = str(self.query_one("#scope", Select).value)
            path = client_config_path(client, scope=scope, project_dir=Path.cwd())
            if client == "codex":
                changed = write_codex_config(path, Path.cwd())
            else:
                changed = write_json_config(path, client, Path.cwd())
        except (OSError, TypeError, ValueError) as exc:
            self._set_status(f"[bold red]Setup failed:[/] {exc}")
            return
        state = "updated" if changed else "already current"
        self._set_status(
            "[bold green]Configured.[/] "
            f"API key: {storage}; {SCOPE_LABELS[scope]} {client_label(client)} "
            f"config: {state}. Restart {client_label(client)} to reload the MCP."
        )

    async def _test_connection(self) -> None:
        try:
            settings = DreamMSSettings.from_env()
            async with DreamMSClient(settings) as client:
                await client.get("/api/v1/usage")
        except DreamMSError as exc:
            self._set_status(f"[bold red]Connection failed:[/] {exc.public_message}")
        except Exception:  # noqa: BLE001 - hide unexpected details in the TUI
            self._set_status("[bold red]Connection failed:[/] DreamMS was unreachable.")
        else:
            self._set_status("[bold green]Connected.[/] DreamMS accepted the API key.")


def main() -> None:
    """Run the setup wizard."""

    SetupWizard().run()
