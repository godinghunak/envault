"""Key rotation: re-encrypt all vault versions with a new password."""

from pathlib import Path
from envault.vault import _vault_path, load_manifest, save_manifest
from envault.crypto import encrypt_file, decrypt_file


def rotate_password(vault_dir: str, old_password: str, new_password: str) -> list[int]:
    """Re-encrypt every stored version with a new password.

    Returns list of version numbers that were rotated.
    """
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        return []

    rotated = []
    vault = Path(_vault_path(vault_dir))

    for entry in versions:
        ver = entry["version"]
        enc_path = vault / f"v{ver}.env.enc"
        if not enc_path.exists():
            continue

        # Decrypt with old password, re-encrypt with new
        plaintext = decrypt_file(str(enc_path), old_password)
        encrypt_file(plaintext, str(enc_path), new_password)
        rotated.append(ver)

    return rotated


def rotate_single_version(vault_dir: str, version: int, old_password: str, new_password: str) -> bool:
    """Re-encrypt a single version. Returns True on success."""
    vault = Path(_vault_path(vault_dir))
    enc_path = vault / f"v{version}.env.enc"
    if not enc_path.exists():
        raise FileNotFoundError(f"Version {version} not found.")

    plaintext = decrypt_file(str(enc_path), old_password)
    encrypt_file(plaintext, str(enc_path), new_password)
    return True
