"""Rollback support: restore a previous version of a .env file."""

import os
from envault.vault import _vault_path, load_manifest, get_version
from envault.crypto import decrypt_file
from envault.audit import log_event


def rollback(vault_dir: str, env_name: str, target_version: int, password: str, output_path: str) -> None:
    """Decrypt and restore a specific version to output_path."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get(env_name, [])

    if not versions:
        raise ValueError(f"No versions found for '{env_name}'")

    available = [v["version"] for v in versions]
    if target_version not in available:
        raise ValueError(
            f"Version {target_version} not found for '{env_name}'. Available: {available}"
        )

    version_entry = next(v for v in versions if v["version"] == target_version)
    encrypted_path = os.path.join(_vault_path(vault_dir), version_entry["file"])

    if not os.path.exists(encrypted_path):
        raise FileNotFoundError(f"Encrypted file not found: {encrypted_path}")

    plaintext = decrypt_file(encrypted_path, password)

    with open(output_path, "wb") as f:
        f.write(plaintext)

    log_event(vault_dir, "rollback", {
        "env": env_name,
        "target_version": target_version,
        "output": output_path,
    })


def list_versions(vault_dir: str, env_name: str) -> list:
    """Return list of version metadata dicts for env_name."""
    manifest = load_manifest(vault_dir)
    return manifest.get(env_name, [])
