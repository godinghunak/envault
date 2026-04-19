"""Archive and restore vault versions to/from a single portable file."""

import json
import base64
from pathlib import Path
from envault.vault import _vault_path, load_manifest, list_versions, get_version


def _archive_path(vault_dir: str, name: str) -> Path:
    return Path(vault_dir) / ".envault" / "archives" / f"{name}.evarchive"


def create_archive(vault_dir: str, name: str, versions: list[int] | None = None) -> Path:
    """Bundle selected (or all) encrypted version blobs into an archive file."""
    manifest = load_manifest(vault_dir)
    all_versions = list_versions(vault_dir)
    if not all_versions:
        raise ValueError("No versions to archive.")

    target_versions = versions if versions is not None else all_versions
    for v in target_versions:
        if v not in all_versions:
            raise ValueError(f"Version {v} does not exist.")

    entries = {}
    for v in target_versions:
        blob = get_version(vault_dir, v)
        entries[str(v)] = base64.b64encode(blob).decode()

    archive = {
        "versions": entries,
        "manifest_versions": [
            m for m in manifest.get("versions", []) if m["version"] in target_versions
        ],
    }

    path = _archive_path(vault_dir, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(archive, indent=2))
    return path


def list_archives(vault_dir: str) -> list[str]:
    """Return names of all archives."""
    d = Path(vault_dir) / ".envault" / "archives"
    if not d.exists():
        return []
    return [p.stem for p in sorted(d.glob("*.evarchive"))]


def load_archive(vault_dir: str, name: str) -> dict:
    """Load and parse an archive by name."""
    path = _archive_path(vault_dir, name)
    if not path.exists():
        raise FileNotFoundError(f"Archive '{name}' not found.")
    return json.loads(path.read_text())


def delete_archive(vault_dir: str, name: str) -> None:
    """Delete an archive file."""
    path = _archive_path(vault_dir, name)
    if not path.exists():
        raise FileNotFoundError(f"Archive '{name}' not found.")
    path.unlink()
