"""Extract a subset of keys from a vault version into a new version or file."""

from __future__ import annotations

from typing import Optional

from envault.crypto import decrypt_file, encrypt_file
from envault.diff import parse_env
from envault.vault import load_manifest, add_version, _vault_path


class ExtractionError(Exception):
    pass


def extract_keys(
    env_dict: dict[str, str],
    keys: list[str],
    *,
    missing_ok: bool = False,
) -> dict[str, str]:
    """Return a new dict containing only the requested keys."""
    result: dict[str, str] = {}
    for key in keys:
        if key in env_dict:
            result[key] = env_dict[key]
        elif not missing_ok:
            raise ExtractionError(f"Key not found: {key!r}")
    return result


def extract_version(
    vault_dir: str,
    password: str,
    keys: list[str],
    version: Optional[int] = None,
    *,
    missing_ok: bool = False,
) -> str:
    """Decrypt *version* (latest if None), extract *keys*, re-encrypt and save
    as a new version.  Returns the plaintext of the extracted content."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ExtractionError("Vault is empty")

    if version is None:
        version = max(v["version"] for v in versions)

    entry = next((v for v in versions if v["version"] == version), None)
    if entry is None:
        raise ExtractionError(f"Version {version} not found")

    vault_path = _vault_path(vault_dir)
    encrypted_path = vault_path / entry["file"]
    plaintext = decrypt_file(str(encrypted_path), password)
    env_dict = parse_env(plaintext)
    extracted = extract_keys(env_dict, keys, missing_ok=missing_ok)
    new_text = "".join(f"{k}={v}\n" for k, v in extracted.items())
    new_version = add_version(vault_dir, new_text, password)
    return new_text


def extract_to_file(
    vault_dir: str,
    password: str,
    keys: list[str],
    dest: str,
    version: Optional[int] = None,
    *,
    missing_ok: bool = False,
) -> str:
    """Extract *keys* from *version* and write plaintext to *dest*."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ExtractionError("Vault is empty")

    if version is None:
        version = max(v["version"] for v in versions)

    entry = next((v for v in versions if v["version"] == version), None)
    if entry is None:
        raise ExtractionError(f"Version {version} not found")

    vault_path = _vault_path(vault_dir)
    encrypted_path = vault_path / entry["file"]
    plaintext = decrypt_file(str(encrypted_path), password)
    env_dict = parse_env(plaintext)
    extracted = extract_keys(env_dict, keys, missing_ok=missing_ok)
    new_text = "".join(f"{k}={v}\n" for k, v in extracted.items())
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    return new_text
