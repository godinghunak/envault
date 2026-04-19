"""Sign and verify vault versions using HMAC-SHA256."""
import hashlib
import hmac
import json
from pathlib import Path
from datetime import datetime, timezone

from envault.vault import _vault_path


def _sigs_path(vault_dir: str) -> Path:
    return _vault_path(vault_dir) / "signatures.json"


def load_signatures(vault_dir: str) -> dict:
    p = _sigs_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_signatures(vault_dir: str, sigs: dict) -> None:
    _sigs_path(vault_dir).write_text(json.dumps(sigs, indent=2))


def _compute_hmac(data: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), data, hashlib.sha256).hexdigest()


def sign_version(vault_dir: str, version: int, data: bytes, secret: str) -> str:
    """Sign a version's raw encrypted data and store the signature."""
    sig = _compute_hmac(data, secret)
    sigs = load_signatures(vault_dir)
    sigs[str(version)] = {
        "signature": sig,
        "signed_at": datetime.now(timezone.utc).isoformat(),
    }
    save_signatures(vault_dir, sigs)
    return sig


def verify_version(vault_dir: str, version: int, data: bytes, secret: str) -> bool:
    """Verify a version's signature. Returns True if valid."""
    sigs = load_signatures(vault_dir)
    entry = sigs.get(str(version))
    if entry is None:
        raise KeyError(f"No signature found for version {version}")
    expected = _compute_hmac(data, secret)
    return hmac.compare_digest(expected, entry["signature"])


def get_signature_entry(vault_dir: str, version: int) -> dict | None:
    sigs = load_signatures(vault_dir)
    return sigs.get(str(version))


def remove_signature(vault_dir: str, version: int) -> bool:
    sigs = load_signatures(vault_dir)
    key = str(version)
    if key not in sigs:
        return False
    del sigs[key]
    save_signatures(vault_dir, sigs)
    return True
