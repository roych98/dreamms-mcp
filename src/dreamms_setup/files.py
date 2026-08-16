"""Safe config-file writing with one-time backups."""

from __future__ import annotations

from pathlib import Path


def write_config_text(config_path: Path, previous: str, updated: str) -> bool:
    """Write changed config text and preserve the original once."""

    if updated == previous:
        return False
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists():
        backup_path = config_path.with_suffix(config_path.suffix + ".dreamms-backup")
        if not backup_path.exists():
            backup_path.write_text(previous, encoding="utf-8")
    config_path.write_text(updated, encoding="utf-8", newline="\n")
    return True
