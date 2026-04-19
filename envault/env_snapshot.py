"""Snapshot support: export a named point-in-time copy of the vault state."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from envault.vault import _vault_path, load_manifest
from envault.export import export_version, export_latest


def _snapshots_path(vault_dir: str) -> Path:
    return _vault_path(vault_dir) / "snapshots.json"


def load_snapshots(vault_dir: str) -> dict:
    p = _snapshots_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_snapshots(vault_dir: str, data: dict) -> None:
    _snapshots_path(vault_dir).write_text(json.dumps(data, indent=2))


def create_snapshot(vault_dir: str, name: str, password: str, version: int | None = None) -> int:
    """Create a named snapshot. Returns the version captured."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions available to snapshot.")

    if version is None:
        version = max(versions)
    elif version not in versions:
        raise ValueError(f"Version {version} does not exist.")

    content = export_version(vault_dir, version, password)
    snapshots = load_snapshots(vault_dir)
    snapshots[name] = {
        "version": version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "content": content,
    }
    save_snapshots(vault_dir, snapshots)
    return version


def get_snapshot(vault_dir: str, name: str) -> dict:
    snapshots = load_snapshots(vault_dir)
    if name not in snapshots:
        raise KeyError(f"Snapshot '{name}' not found.")
    return snapshots[name]


def delete_snapshot(vault_dir: str, name: str) -> None:
    snapshots = load_snapshots(vault_dir)
    if name not in snapshots:
        raise KeyError(f"Snapshot '{name}' not found.")
    del snapshots[name]
    save_snapshots(vault_dir, snapshots)


def list_snapshots(vault_dir: str) -> list[str]:
    return list(load_snapshots(vault_dir).keys())
