"""Encryption and decryption utilities for .env files using Fernet symmetric encryption."""

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


SALT_SIZE = 16
ITERATIONS = 390000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt(plaintext: str, password: str) -> bytes:
    """
    Encrypt plaintext using a password.
    Returns salt + encrypted token as raw bytes.
    """
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    token = Fernet(key).encrypt(plaintext.encode())
    return salt + token


def decrypt(data: bytes, password: str) -> str:
    """
    Decrypt data previously encrypted with `encrypt`.
    Raises ValueError on bad password or corrupted data.
    """
    salt = data[:SALT_SIZE]
    token = data[SALT_SIZE:]
    key = derive_key(password, salt)
    try:
        return Fernet(key).decrypt(token).decode()
    except InvalidToken:
        raise ValueError("Decryption failed: invalid password or corrupted data.")


def encrypt_file(src_path: str, dest_path: str, password: str) -> None:
    """Read a plaintext file, encrypt it, and write to dest_path."""
    with open(src_path, "r") as f:
        plaintext = f.read()
    encrypted = encrypt(plaintext, password)
    with open(dest_path, "wb") as f:
        f.write(encrypted)


def decrypt_file(src_path: str, dest_path: str, password: str) -> None:
    """Read an encrypted file, decrypt it, and write plaintext to dest_path."""
    with open(src_path, "rb") as f:
        data = f.read()
    plaintext = decrypt(data, password)
    with open(dest_path, "w") as f:
        f.write(plaintext)
