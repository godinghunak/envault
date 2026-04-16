"""Tests for envault.crypto encryption/decryption utilities."""

import os
import pytest
import tempfile

from envault.crypto import encrypt, decrypt, encrypt_file, decrypt_file


PASSWORD = "super-secret-password"
PLAINTEXT = "DB_HOST=localhost\nDB_PASSWORD=hunter2\nAPI_KEY=abc123\n"


def test_encrypt_returns_bytes():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, bytes)


def test_encrypt_decrypt_roundtrip():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    decrypted = decrypt(encrypted, PASSWORD)
    assert decrypted == PLAINTEXT


def test_decrypt_wrong_password_raises():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(encrypted, "wrong-password")


def test_encrypt_produces_different_ciphertext_each_time():
    """Each encryption uses a random salt, so output should differ."""
    enc1 = encrypt(PLAINTEXT, PASSWORD)
    enc2 = encrypt(PLAINTEXT, PASSWORD)
    assert enc1 != enc2


def test_decrypt_corrupted_data_raises():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    corrupted = encrypted[:-10] + b"\x00" * 10
    with pytest.raises(ValueError):
        decrypt(corrupted, PASSWORD)


def test_encrypt_file_decrypt_file_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, ".env")
        enc = os.path.join(tmpdir, ".env.vault")
        out = os.path.join(tmpdir, ".env.decrypted")

        with open(src, "w") as f:
            f.write(PLAINTEXT)

        encrypt_file(src, enc, PASSWORD)
        assert os.path.exists(enc)

        decrypt_file(enc, out, PASSWORD)
        with open(out, "r") as f:
            result = f.read()

        assert result == PLAINTEXT


def test_encrypt_file_wrong_password_raises():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, ".env")
        enc = os.path.join(tmpdir, ".env.vault")
        out = os.path.join(tmpdir, ".env.out")

        with open(src, "w") as f:
            f.write(PLAINTEXT)

        encrypt_file(src, enc, PASSWORD)

        with pytest.raises(ValueError):
            decrypt_file(enc, out, "bad-password")
