"""Team sharing support: export/import vault keys encrypted for recipients."""

import json
import os
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


def generate_keypair() -> tuple[bytes, bytes]:
    """Generate an X25519 keypair. Returns (private_pem, public_pem)."""
    private_key = X25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def _derive_shared_fernet(shared_secret: bytes) -> Fernet:
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"envault-share")
    key = hkdf.derive(shared_secret)
    return Fernet(b64encode(key))


def encrypt_secret_for_recipient(secret: bytes, recipient_public_pem: bytes) -> str:
    """Encrypt a vault secret (e.g. password) for a recipient's public key."""
    recipient_pub = serialization.load_pem_public_key(recipient_public_pem)
    ephemeral_private = X25519PrivateKey.generate()
    shared_secret = ephemeral_private.exchange(recipient_pub)
    fernet = _derive_shared_fernet(shared_secret)
    encrypted = fernet.encrypt(secret)
    ephemeral_pub_pem = ephemeral_private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    payload = {
        "ephemeral_pub": b64encode(ephemeral_pub_pem).decode(),
        "ciphertext": b64encode(encrypted).decode(),
    }
    return json.dumps(payload)


def decrypt_secret_from_sender(payload_json: str, recipient_private_pem: bytes) -> bytes:
    """Decrypt a vault secret using the recipient's private key.

    Raises:
        ValueError: If the payload is malformed or decryption fails.
    """
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid sharing payload: {e}") from e

    if "ephemeral_pub" not in payload or "ciphertext" not in payload:
        raise ValueError("Sharing payload is missing required fields.")

    try:
        ephemeral_pub_pem = b64decode(payload["ephemeral_pub"])
        ciphertext = b64decode(payload["ciphertext"])
    except Exception as e:
        raise ValueError(f"Failed to decode payload fields: {e}") from e

    recipient_priv = serialization.load_pem_private_key(recipient_private_pem, password=None)
    ephemeral_pub = serialization.load_pem_public_key(ephemeral_pub_pem)
    shared_secret = recipient_priv.exchange(ephemeral_pub)
    fernet = _derive_shared_fernet(shared_secret)

    try:
        return fernet.decrypt(ciphertext)
    except InvalidToken as e:
        raise ValueError("Decryption failed: invalid key or corrupted ciphertext.") from e
