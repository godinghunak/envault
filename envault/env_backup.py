"""Backup and restore vault snapshots to/from external archive files."""

import json
import tarfile
import io
from pathlib import Path
from datetime import datetime

from envault.vault import _vault_path, load_manifest


def create_backup(vault_dir: str, dest_path: str) -> str:
    """Create a .tar.gz backup of the entire vault directory."""
    vault = Path(vault_dir)
    if not vault.exists():
        raise FileNotFoundError(f"Vault not found: {vault_dir}")

    dest = Path(dest_path)
    with tarfile.open(dest, "w:gz") as tar:
        tar.add(vault, arcname="vault")

    return str(dest)


def restore_backup(backup_path: str, dest_dir: str, overwrite: bool = False) -> str:
    """Restore a vault from a .tar.gz backup file."""
    src = Path(backup_path)
    if not src.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    dest = Path(dest_dir)
    if dest.exists() and not overwrite:
        raise FileExistsError(
            f"Destination already exists: {dest_dir}. Use overwrite=True to replace."
        )

    dest.mkdir(parents=True, exist_ok=True)

    with tarfile.open(src, "r:gz") as tar:
        members = tar.getmembers()
        for member in members:
            # Strip leading 'vault/' prefix
            parts = Path(member.name).parts
            if len(parts) > 1:
                member.name = str(Path(*parts[1:]))
            elif len(parts) == 1 and parts[0] == "vault":
                continue
            tar.extract(member, path=dest)

    return str(dest)


def backup_info(backup_path: str) -> dict:
    """Return metadata about a backup archive."""
    src = Path(backup_path)
    if not src.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    stat = src.stat()
    info = {
        "path": str(src.resolve()),
        "size_bytes": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "files": [],
    }

    with tarfile.open(src, "r:gz") as tar:
        info["files"] = [m.name for m in tar.getmembers() if m.isfile()]

    return info
