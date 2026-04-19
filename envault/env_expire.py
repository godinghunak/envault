"""Version expiry: mark versions with a TTL and check/purge expired ones."""

import json
import time
from pathlib import Path
from envault.vault import _vault_path, load_manifest


def _expiry_path(vault_dir: str) -> Path:
    return _vault_path(vault_dir) / "expiry.json"


def load_expiry(vault_dir: str) -> dict:
    p = _expiry_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_expiry(vault_dir: str, data: dict) -> None:
    _expiry_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_expiry(vault_dir: str, version: int, ttl_seconds: int) -> float:
    """Set expiry for a version. Returns the absolute expiry timestamp."""
    manifest = load_manifest(vault_dir)
    versions = [e["version"] for e in manifest.get("versions", [])]
    if version not in versions:
        raise ValueError(f"Version {version} does not exist")
    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be positive")
    expires_at = time.time() + ttl_seconds
    data = load_expiry(vault_dir)
    data[str(version)] = expires_at
    save_expiry(vault_dir, data)
    return expires_at


def get_expiry(vault_dir: str, version: int) -> float | None:
    data = load_expiry(vault_dir)
    val = data.get(str(version))
    return float(val) if val is not None else None


def is_expired(vault_dir: str, version: int) -> bool:
    exp = get_expiry(vault_dir, version)
    if exp is None:
        return False
    return time.time() > exp


def list_expired(vault_dir: str) -> list[int]:
    data = load_expiry(vault_dir)
    now = time.time()
    return [int(v) for v, ts in data.items() if now > float(ts)]


def clear_expiry(vault_dir: str, version: int) -> bool:
    data = load_expiry(vault_dir)
    key = str(version)
    if key not in data:
        return False
    del data[key]
    save_expiry(vault_dir, data)
    return True
