"""Batch decrypt all versions from the vault."""

from pathlib import Path
from typing import List, Tuple

from envault.vault import load_manifest, _vault_path
from envault.crypto import decrypt_file


def decrypt_all_versions(
    vault_dir: str, password: str
) -> List[Tuple[int, str]]:
    """
    Decrypt every version stored in the vault.

    Returns a list of (version, plaintext) tuples sorted by version.
    Raises ValueError if any version fails to decrypt.
    """
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        return []

    results = []
    vault = Path(_vault_path(vault_dir))
    for version in sorted(versions):
        enc_path = vault / f"v{version}.env.enc"
        if not enc_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {enc_path}")
        plaintext = decrypt_file(str(enc_path), password)
        results.append((version, plaintext))
    return results


def decrypt_version(
    vault_dir: str, version: int, password: str
) -> str:
    """Decrypt a single specific version."""
    vault = Path(_vault_path(vault_dir))
    enc_path = vault / f"v{version}.env.enc"
    if not enc_path.exists():
        raise FileNotFoundError(f"Version {version} not found.")
    return decrypt_file(str(enc_path), password)


def list_decryptable_versions(vault_dir: str, password: str) -> List[int]:
    """
    Return list of version numbers that can be decrypted with the given password.
    Silently skips versions that fail.
    """
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    decryptable = []
    vault = Path(_vault_path(vault_dir))
    for version in sorted(versions):
        enc_path = vault / f"v{version}.env.enc"
        try:
            decrypt_file(str(enc_path), password)
            decryptable.append(version)
        except Exception:
            pass
    return decryptable
