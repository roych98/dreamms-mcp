from __future__ import annotations

import pytest

from dreamms_mcp.config import DEFAULT_API_BASE_URL, DreamMSSettings
from dreamms_mcp.errors import DreamMSConfigurationError


def test_settings_load_key_and_default_url(monkeypatch):
    monkeypatch.setenv("DREAM_API_KEY", "  my-key  ")
    monkeypatch.delenv("DREAM_API_BASE_URL", raising=False)

    settings = DreamMSSettings.from_env()

    assert settings.api_key == "my-key"
    assert settings.base_url == DEFAULT_API_BASE_URL
    assert "my-key" not in repr(settings)
    assert "redacted" in repr(settings)


def test_missing_key_is_rejected(monkeypatch):
    monkeypatch.delenv("DREAM_API_KEY", raising=False)
    with pytest.raises(DreamMSConfigurationError, match="DREAM_API_KEY"):
        DreamMSSettings.from_env()


@pytest.mark.parametrize(
    "base_url", ["not-a-url", "ftp://dreamms.gg", "https://dreamms.gg?key=secret"]
)
def test_invalid_base_url_is_rejected(monkeypatch, base_url):
    monkeypatch.setenv("DREAM_API_KEY", "key")
    monkeypatch.setenv("DREAM_API_BASE_URL", base_url)
    with pytest.raises(DreamMSConfigurationError):
        DreamMSSettings.from_env()
