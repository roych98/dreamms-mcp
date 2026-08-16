from __future__ import annotations

from pathlib import Path

import pytest
from textual.widgets import Input, Select, Static

from dreamms_setup.app import SetupWizard
from dreamms_setup.paths import client_config_path


@pytest.mark.asyncio
async def test_setup_wizard_mounts_and_can_quit():
    async with SetupWizard().run_test() as pilot:
        assert pilot.app.query_one("#config-path", Static).render().plain == str(
            client_config_path("codex", scope="user", project_dir=Path.cwd())
        )
        assert pilot.app.query_one("#discord-id", Input).placeholder == (
            "Your numeric Discord user ID for app APIs"
        )
        pilot.app.query_one("#client", Select).value = "pi"
        await pilot.pause()
        assert ".pi" in pilot.app.query_one("#config-path", Static).render().plain
        pilot.app.query_one("#scope", Select).value = "project"
        await pilot.pause()
        assert (
            pilot.app.query_one("#config-path", Static)
            .render()
            .plain.endswith(".mcp.json")
        )
        await pilot.press("ctrl+q")
