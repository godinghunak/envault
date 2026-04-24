"""Track deprecated keys in the vault with optional replacement suggestions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _deprecations_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault" / "deprecations.json"


def load_deprecations(vault_dir: str) -> Dict[str, dict]:
    path = _deprecations_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_deprecations(vault_dir: str, data: Dict[str, dict]) -> None:
    path = _deprecations_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def deprecate_key(
    vault_dir: str,
    key: str,
    reason: str = "",
    replacement: Optional[str] = None,
) -> None:
    if not key:
        raise ValueError("Key must not be empty.")
    data = load_deprecations(vault_dir)
    data[key] = {"reason": reason, "replacement": replacement}
    save_deprecations(vault_dir, data)


def undeprecate_key(vault_dir: str, key: str) -> None:
    data = load_deprecations(vault_dir)
    data.pop(key, None)
    save_deprecations(vault_dir, data)


def list_deprecated(vault_dir: str) -> List[str]:
    return list(load_deprecations(vault_dir).keys())


def get_deprecation(vault_dir: str, key: str) -> Optional[dict]:
    return load_deprecations(vault_dir).get(key)


def check_env_for_deprecated(
    vault_dir: str, env: Dict[str, str]
) -> List[dict]:
    """Return a list of issues for keys in env that are deprecated."""
    data = load_deprecations(vault_dir)
    issues = []
    for key in env:
        if key in data:
            entry = data[key]
            issues.append(
                {
                    "key": key,
                    "reason": entry.get("reason", ""),
                    "replacement": entry.get("replacement"),
                }
            )
    return issues
