"""Vault management: store and retrieve versioned encrypted .env files."""

import json
import os
import time
from pathlib import Path

DEFAULT_VAULT_DIR = ".envault"
MANIFEST_FILE = "manifest.json"


def _vault_path(vault_dir: str = DEFAULT_VAULT_DIR) -> Path:
    return Path(vault_dir)


def _manifest_path(vault_dir: str = DEFAULT_VAULT_DIR) -> Path:
    return _vault_path(vault_dir) / MANIFEST_FILE


def init_vault(vault_dir: str = DEFAULT_VAULT_DIR) -> None:
    """Initialize the vault directory and manifest."""
    path = _vault_path(vault_dir)
    path.mkdir(parents=True, exist_ok=True)
    manifest_file = _manifest_path(vault_dir)
    if not manifest_file.exists():
        manifest_file.write_text(json.dumps({"versions": []}, indent=2))


def load_manifest(vault_dir: str = DEFAULT_VAULT_DIR) -> dict:
    """Load the vault manifest."""
    manifest_file = _manifest_path(vault_dir)
    if not manifest_file.exists():
        raise FileNotFoundError(f"Vault not initialized at '{vault_dir}'. Run 'envault init'.")
    return json.loads(manifest_file.read_text())


def save_manifest(manifest: dict, vault_dir: str = DEFAULT_VAULT_DIR) -> None:
    """Persist the vault manifest."""
    _manifest_path(vault_dir).write_text(json.dumps(manifest, indent=2))


def add_version(encrypted_path: str, label: str | None = None, vault_dir: str = DEFAULT_VAULT_DIR) -> dict:
    """Register a new encrypted file version in the manifest."""
    manifest = load_manifest(vault_dir)
    version_id = len(manifest["versions"]) + 1
    entry = {
        "id": version_id,
        "file": encrypted_path,
        "label": label or f"v{version_id}",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    manifest["versions"].append(entry)
    save_manifest(manifest, vault_dir)
    return entry


def list_versions(vault_dir: str = DEFAULT_VAULT_DIR) -> list[dict]:
    """Return all registered versions."""
    return load_manifest(vault_dir)["versions"]


def get_version(version_id: int, vault_dir: str = DEFAULT_VAULT_DIR) -> dict:
    """Retrieve a specific version entry by ID."""
    versions = list_versions(vault_dir)
    for v in versions:
        if v["id"] == version_id:
            return v
    raise KeyError(f"Version {version_id} not found in vault.")


def latest_version(vault_dir: str = DEFAULT_VAULT_DIR) -> dict | None:
    """Return the most recently added version, or None if empty."""
    versions = list_versions(vault_dir)
    return versions[-1] if versions else None
