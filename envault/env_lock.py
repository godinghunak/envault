"""Lock file support: record exact key=value snapshot for reproducible deploys."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
from envault.vault import _vault_path, load_manifest
from envault.export import export_latest, export_version
from envault.diff import parse_env


def _lock_path(vault_dir: str) -> Path:
    return _vault_path(vault_dir) / "envault.lock"


def write_lock(vault_dir: str, version: Optional[int] = None) -> dict:
    """Write a lock file capturing the resolved env for a given (or latest) version."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions found in vault.")

    if version is None:
        version = len(versions)

    if version < 1 or version > len(versions):
        raise ValueError(f"Version {version} does not exist.")

    content = export_version(vault_dir, version, manifest["password_hint"] if "password_hint" in manifest else None)
    env = parse_env(content)

    lock_data = {
        "version": version,
        "keys": sorted(env.keys()),
        "checksum": _checksum(content),
    }
    _lock_path(vault_dir).write_text(json.dumps(lock_data, indent=2))
    return lock_data


def read_lock(vault_dir: str) -> dict:
    path = _lock_path(vault_dir)
    if not path.exists():
        raise FileNotFoundError("No envault.lock found. Run 'envault lock write' first.")
    return json.loads(path.read_text())


def verify_lock(vault_dir: str, password: str) -> bool:
    """Return True if current latest version matches the lock file checksum."""
    lock = read_lock(vault_dir)
    locked_version = lock["version"]
    content = export_version(vault_dir, locked_version, password)
    return _checksum(content) == lock["checksum"]


def _checksum(content: str) -> str:
    import hashlib
    return hashlib.sha256(content.encode()).hexdigest()
