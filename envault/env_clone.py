"""Clone a vault version to a new .env file or another vault profile."""
from pathlib import Path
from envault.export import export_version, export_latest
from envault.vault import load_manifest


def clone_version_to_file(vault_dir: str, version: int | None, dest: str, password: str) -> int:
    """Decrypt a vault version and write it to dest path. Returns version cloned."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions in vault.")

    if version is None:
        version = versions[-1]["version"]

    if version not in [v["version"] for v in versions]:
        raise ValueError(f"Version {version} not found in vault.")

    content = export_version(vault_dir, version, password)
    Path(dest).write_text(content)
    return version


def clone_latest_to_file(vault_dir: str, dest: str, password: str) -> int:
    """Decrypt the latest vault version and write it to dest path."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions in vault.")
    latest = versions[-1]["version"]
    content = export_latest(vault_dir, password)
    Path(dest).write_text(content)
    return latest


def list_clone_targets(vault_dir: str) -> list[int]:
    """Return list of available version numbers that can be cloned."""
    manifest = load_manifest(vault_dir)
    return [v["version"] for v in manifest.get("versions", [])]
