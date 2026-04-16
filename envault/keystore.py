"""Manage local keypair storage for the current user."""

import os
from pathlib import Path
from envault.sharing import generate_keypair

DEFAULT_KEYSTORE_DIR = Path.home() / ".envault" / "keys"
PRIVATE_KEY_FILE = "identity.pem"
PUBLIC_KEY_FILE = "identity.pub.pem"


def keystore_dir() -> Path:
    return Path(os.environ.get("ENVAULT_KEYSTORE_DIR", DEFAULT_KEYSTORE_DIR))


def init_keystore() -> Path:
    """Create keystore directory and generate keypair if not present."""
    ks = keystore_dir()
    ks.mkdir(parents=True, exist_ok=True)
    priv_path = ks / PRIVATE_KEY_FILE
    pub_path = ks / PUBLIC_KEY_FILE
    if not priv_path.exists():
        private_pem, public_pem = generate_keypair()
        priv_path.write_bytes(private_pem)
        pub_path.write_bytes(public_pem)
        priv_path.chmod(0o600)
    return ks


def load_private_key() -> bytes:
    path = keystore_dir() / PRIVATE_KEY_FILE
    if not path.exists():
        raise FileNotFoundError("No private key found. Run 'envault keygen' first.")
    return path.read_bytes()


def load_public_key() -> bytes:
    path = keystore_dir() / PUBLIC_KEY_FILE
    if not path.exists():
        raise FileNotFoundError("No public key found. Run 'envault keygen' first.")
    return path.read_bytes()


def public_key_path() -> Path:
    return keystore_dir() / PUBLIC_KEY_FILE
