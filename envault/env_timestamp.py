"""Timestamp utilities for vault versions: record, retrieve, and format push times."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def _timestamps_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".timestamps.json"


def load_timestamps(vault_dir: str) -> dict:
    path = _timestamps_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_timestamps(vault_dir: str, data: dict) -> None:
    _timestamps_path(vault_dir).write_text(json.dumps(data, indent=2))


def record_timestamp(vault_dir: str, version: int, dt: datetime | None = None) -> str:
    """Record a UTC timestamp for the given version. Returns the ISO string stored."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    iso = dt.isoformat()
    data = load_timestamps(vault_dir)
    data[str(version)] = iso
    save_timestamps(vault_dir, data)
    return iso


def get_timestamp(vault_dir: str, version: int) -> str | None:
    """Return the ISO timestamp string for *version*, or None if not recorded."""
    data = load_timestamps(vault_dir)
    return data.get(str(version))


def list_timestamps(vault_dir: str) -> list[tuple[int, str]]:
    """Return a sorted list of (version, iso_timestamp) tuples."""
    data = load_timestamps(vault_dir)
    return sorted((int(k), v) for k, v in data.items())


def format_timestamp(iso: str, fmt: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
    """Convert an ISO timestamp string to a human-readable string."""
    dt = datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime(fmt)


def delete_timestamp(vault_dir: str, version: int) -> bool:
    """Remove the timestamp for *version*. Returns True if it existed."""
    data = load_timestamps(vault_dir)
    key = str(version)
    if key not in data:
        return False
    del data[key]
    save_timestamps(vault_dir, data)
    return True
