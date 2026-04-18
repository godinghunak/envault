"""Export decrypted .env versions to stdout or file."""
from pathlib import Path
from envault.vault import _vault_path, load_manifest, get_version
from envault.crypto import decrypt_file


def export_version(vault_dir: str, version: int, password: str) -> str:
    """Decrypt and return the contents of a specific version."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions found in vault.")

    version_entry = next((v for v in versions if v["version"] == version), None)
    if version_entry is None:
        raise ValueError(f"Version {version} not found.")

    enc_path = Path(vault_dir) / ".envault" / version_entry["file"]
    plaintext = decrypt_file(str(enc_path), password)
    return plaintext.decode()


def export_latest(vault_dir: str, password: str) -> str:
    """Decrypt and return the latest version contents."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions found in vault.")
    latest = max(versions, key=lambda v: v["version"])
    return export_version(vault_dir, latest["version"], password)


def export_to_file(vault_dir: str, version: int, password: str, output_path: str) -> None:
    """Decrypt a version and write it to output_path."""
    content = export_version(vault_dir, version, password)
    Path(output_path).write_text(content)
