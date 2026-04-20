"""Checksum computation and verification for vault versions."""

import hashlib
import json
from pathlib import Path
from typing import Optional

from envault.vault import _vault_path, load_manifest
from envault.crypto import decrypt


def _checksums_path(vault_dir: Path) -> Path:
    return vault_dir / ".checksums.json"


def load_checksums(vault_dir: Path) -> dict:
    p = _checksums_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_checksums(vault_dir: Path, data: dict) -> None:
    _checksums_path(vault_dir).write_text(json.dumps(data, indent=2))


def compute_checksum(data: bytes, algorithm: str = "sha256") -> str:
    """Compute a hex digest checksum of raw bytes."""
    h = hashlib.new(algorithm)
    h.update(data)
    return h.hexdigest()


def record_checksum(vault_dir: Path, version: int, password: str) -> str:
    """Decrypt a version and record its plaintext checksum."""
    enc_path = _vault_path(vault_dir) / f"v{version}.enc"
    if not enc_path.exists():
        raise FileNotFoundError(f"Encrypted file not found: {enc_path}")
    plaintext = decrypt(enc_path.read_bytes(), password)
    checksum = compute_checksum(plaintext)
    data = load_checksums(vault_dir)
    data[str(version)] = {"algorithm": "sha256", "checksum": checksum}
    save_checksums(vault_dir, data)
    return checksum


def verify_checksum(vault_dir: Path, version: int, password: str) -> bool:
    """Verify a version's plaintext matches its recorded checksum."""
    data = load_checksums(vault_dir)
    entry = data.get(str(version))
    if entry is None:
        raise KeyError(f"No checksum recorded for version {version}")
    enc_path = _vault_path(vault_dir) / f"v{version}.enc"
    plaintext = decrypt(enc_path.read_bytes(), password)
    current = compute_checksum(plaintext, entry["algorithm"])
    return current == entry["checksum"]


def get_checksum(vault_dir: Path, version: int) -> Optional[dict]:
    """Return the stored checksum entry for a version, or None."""
    return load_checksums(vault_dir).get(str(version))
