"""Immutable version tracking — mark versions as immutable to prevent overwrite."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envault.vault import _vault_path


def _immutable_path(vault_dir: str) -> Path:
    return _vault_path(vault_dir) / "immutable.json"


def load_immutable(vault_dir: str) -> Dict[int, str]:
    """Return mapping of {version: reason} for all immutable versions."""
    p = _immutable_path(vault_dir)
    if not p.exists():
        return {}
    data = json.loads(p.read_text())
    return {int(k): v for k, v in data.items()}


def save_immutable(vault_dir: str, records: Dict[int, str]) -> None:
    p = _immutable_path(vault_dir)
    p.write_text(json.dumps({str(k): v for k, v in records.items()}, indent=2))


def lock_version(vault_dir: str, version: int, reason: str = "") -> None:
    """Mark *version* as immutable with an optional reason."""
    records = load_immutable(vault_dir)
    records[version] = reason
    save_immutable(vault_dir, records)


def unlock_version(vault_dir: str, version: int) -> None:
    """Remove the immutable lock from *version*."""
    records = load_immutable(vault_dir)
    records.pop(version, None)
    save_immutable(vault_dir, records)


def is_immutable(vault_dir: str, version: int) -> bool:
    """Return True if *version* is currently locked."""
    return version in load_immutable(vault_dir)


def list_immutable(vault_dir: str) -> List[int]:
    """Return a sorted list of all immutable version numbers."""
    return sorted(load_immutable(vault_dir).keys())


def assert_mutable(vault_dir: str, version: int) -> None:
    """Raise ValueError if *version* is immutable."""
    records = load_immutable(vault_dir)
    if version in records:
        reason = records[version]
        msg = f"Version {version} is immutable"
        if reason:
            msg += f": {reason}"
        raise ValueError(msg)
