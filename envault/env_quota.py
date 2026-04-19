"""Vault quota enforcement: limit number of versions stored."""

import json
from pathlib import Path

DEFAULT_MAX_VERSIONS = 50


def _quota_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".quota.json"


def load_quota(vault_dir: str) -> dict:
    p = _quota_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_quota(vault_dir: str, data: dict) -> None:
    _quota_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_quota(vault_dir: str, max_versions: int) -> None:
    if max_versions < 1:
        raise ValueError("max_versions must be at least 1")
    data = load_quota(vault_dir)
    data["max_versions"] = max_versions
    save_quota(vault_dir, data)


def get_quota(vault_dir: str) -> int:
    data = load_quota(vault_dir)
    return data.get("max_versions", DEFAULT_MAX_VERSIONS)


def clear_quota(vault_dir: str) -> None:
    data = load_quota(vault_dir)
    data.pop("max_versions", None)
    save_quota(vault_dir, data)


def check_quota(vault_dir: str, current_version_count: int) -> tuple[bool, int]:
    """Returns (within_quota, max_versions)."""
    max_v = get_quota(vault_dir)
    return current_version_count < max_v, max_v


def enforce_quota(vault_dir: str, current_version_count: int) -> None:
    """Raise if quota would be exceeded."""
    ok, max_v = check_quota(vault_dir, current_version_count)
    if not ok:
        raise RuntimeError(
            f"Quota exceeded: vault already has {current_version_count} versions "
            f"(max {max_v}). Remove old versions or increase the quota."
        )
