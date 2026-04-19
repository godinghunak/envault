"""Prune old vault versions, keeping only the N most recent."""

from pathlib import Path
from envault.vault import load_manifest, save_manifest, _vault_path


def prune_versions(vault_dir: str, password: str, keep: int = 5) -> list[int]:
    """Delete all but the `keep` most recent versions. Returns list of pruned version numbers."""
    if keep < 1:
        raise ValueError("keep must be >= 1")

    manifest = load_manifest(vault_dir)
    versions = sorted(manifest.get("versions", []))

    if len(versions) <= keep:
        return []

    to_prune = versions[: len(versions) - keep]
    vault = Path(_vault_path(vault_dir))

    for v in to_prune:
        enc_file = vault / f"v{v}.enc"
        if enc_file.exists():
            enc_file.unlink()

    remaining = versions[len(versions) - keep :]
    manifest["versions"] = remaining
    save_manifest(vault_dir, manifest)

    return to_prune


def prune_preview(vault_dir: str, keep: int = 5) -> dict:
    """Return a preview of what would be pruned without making changes."""
    if keep < 1:
        raise ValueError("keep must be >= 1")

    manifest = load_manifest(vault_dir)
    versions = sorted(manifest.get("versions", []))

    if len(versions) <= keep:
        return {"to_prune": [], "to_keep": versions}

    to_prune = versions[: len(versions) - keep]
    to_keep = versions[len(versions) - keep :]
    return {"to_prune": to_prune, "to_keep": to_keep}
