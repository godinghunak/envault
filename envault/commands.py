"""High-level CLI command implementations for envault."""

import os
from pathlib import Path

from envault.crypto import encrypt_file, decrypt_file
from envault import vault

DEFAULT_VAULT_DIR = vault.DEFAULT_VAULT_DIR


def cmd_init(vault_dir: str = DEFAULT_VAULT_DIR) -> str:
    """Initialize a new vault."""
    vault.init_vault(vault_dir)
    return f"Vault initialized at '{vault_dir}'."


def cmd_push(env_file: str, password: str, label: str | None = None, vault_dir: str = DEFAULT_VAULT_DIR) -> str:
    """Encrypt and store a new version of the .env file."""
    vault.init_vault(vault_dir)
    versions = vault.list_versions(vault_dir)
    version_id = len(versions) + 1
    encrypted_filename = f"env_v{version_id}.enc"
    encrypted_path = str(Path(vault_dir) / encrypted_filename)

    encrypt_file(env_file, encrypted_path, password)
    entry = vault.add_version(encrypted_filename, label=label, vault_dir=vault_dir)
    return f"Pushed '{env_file}' as version {entry['id']} ({entry['label']})."


def cmd_pull(
    output_file: str,
    password: str,
    version_id: int | None = None,
    vault_dir: str = DEFAULT_VAULT_DIR,
) -> str:
    """Decrypt and restore a version of the .env file."""
    if version_id is not None:
        entry = vault.get_version(version_id, vault_dir)
    else:
        entry = vault.latest_version(vault_dir)
        if entry is None:
            raise RuntimeError("No versions found in vault.")

    encrypted_path = str(Path(vault_dir) / entry["file"])
    decrypt_file(encrypted_path, output_file, password)
    return f"Pulled version {entry['id']} ({entry['label']}) to '{output_file}'."


def cmd_list(vault_dir: str = DEFAULT_VAULT_DIR) -> list[dict]:
    """Return all stored versions."""
    return vault.list_versions(vault_dir)
