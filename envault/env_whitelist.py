"""Whitelist management: restrict which keys are allowed in a vault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional


def _whitelist_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault" / "whitelist.json"


def load_whitelist(vault_dir: str) -> List[str]:
    """Return the list of allowed keys, or empty list if none configured."""
    path = _whitelist_path(vault_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save_whitelist(vault_dir: str, keys: List[str]) -> None:
    path = _whitelist_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(set(keys)), indent=2))


def add_key(vault_dir: str, key: str) -> None:
    """Add a key to the whitelist."""
    key = key.strip()
    if not key:
        raise ValueError("Key must not be empty.")
    keys = load_whitelist(vault_dir)
    if key not in keys:
        keys.append(key)
    save_whitelist(vault_dir, keys)


def remove_key(vault_dir: str, key: str) -> bool:
    """Remove a key from the whitelist. Returns True if it was present."""
    keys = load_whitelist(vault_dir)
    if key in keys:
        keys.remove(key)
        save_whitelist(vault_dir, keys)
        return True
    return False


class WhitelistViolation:
    def __init__(self, key: str):
        self.key = key

    def __str__(self) -> str:
        return f"Key '{self.key}' is not in the whitelist."


def check_env(
    vault_dir: str, env: dict
) -> List[WhitelistViolation]:
    """Return violations for any key in *env* not present in the whitelist.
    If the whitelist is empty (not configured), no violations are raised.
    """
    allowed = load_whitelist(vault_dir)
    if not allowed:
        return []
    allowed_set = set(allowed)
    return [
        WhitelistViolation(k) for k in env if k not in allowed_set
    ]
