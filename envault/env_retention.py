"""Retention policy management for vault versions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _retention_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault" / "retention.json"


def load_retention(vault_dir: str) -> dict:
    path = _retention_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_retention(vault_dir: str, data: dict) -> None:
    path = _retention_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_policy(vault_dir: str, max_versions: int, min_keep: int = 1) -> None:
    if max_versions < 1:
        raise ValueError("max_versions must be at least 1")
    if min_keep < 1:
        raise ValueError("min_keep must be at least 1")
    if min_keep > max_versions:
        raise ValueError("min_keep cannot exceed max_versions")
    data = load_retention(vault_dir)
    data["max_versions"] = max_versions
    data["min_keep"] = min_keep
    save_retention(vault_dir, data)


def get_policy(vault_dir: str) -> Optional[dict]:
    data = load_retention(vault_dir)
    if "max_versions" not in data:
        return None
    return {
        "max_versions": data["max_versions"],
        "min_keep": data.get("min_keep", 1),
    }


def clear_policy(vault_dir: str) -> None:
    path = _retention_path(vault_dir)
    if path.exists():
        path.unlink()


def apply_retention(vault_dir: str, versions: list[int]) -> list[int]:
    """Return list of version numbers that should be pruned per retention policy."""
    policy = get_policy(vault_dir)
    if policy is None:
        return []
    sorted_versions = sorted(versions)
    max_v = policy["max_versions"]
    min_keep = policy["min_keep"]
    keep_count = max(min_keep, len(sorted_versions) - max_v)
    to_prune = sorted_versions[: len(sorted_versions) - keep_count]
    # Always keep at least min_keep newest
    must_keep = sorted_versions[-min_keep:]
    return [v for v in to_prune if v not in must_keep]
