"""Tests for envault.sharing and envault.keystore."""

import os
import pytest
from envault.sharing import (
    generate_keypair,
    encrypt_secret_for_recipient,
    decrypt_secret_from_sender,
)
from envault.keystore import init_keystore, load_private_key, load_public_key


def test_generate_keypair_returns_pem_bytes():
    priv, pub = generate_keypair()
    assert priv.startswith(b"-----BEGIN PRIVATE KEY-----")
    assert pub.startswith(b"-----BEGIN PUBLIC KEY-----")


def test_encrypt_decrypt_roundtrip():
    priv, pub = generate_keypair()
    secret = b"super-secret-vault-password"
    payload = encrypt_secret_for_recipient(secret, pub)
    recovered = decrypt_secret_from_sender(payload, priv)
    assert recovered == secret


def test_different_recipients_cannot_decrypt():
    _, pub_alice = generate_keypair()
    priv_bob, _ = generate_keypair()
    secret = b"only-for-alice"
    payload = encrypt_secret_for_recipient(secret, pub_alice)
    with pytest.raises(Exception):
        decrypt_secret_from_sender(payload, priv_bob)


def test_encrypt_produces_different_ciphertext():
    _, pub = generate_keypair()
    secret = b"same-secret"
    p1 = encrypt_secret_for_recipient(secret, pub)
    p2 = encrypt_secret_for_recipient(secret, pub)
    assert p1 != p2


def test_init_keystore_creates_files(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_KEYSTORE_DIR", str(tmp_path / "keys"))
    import importlib
    import envault.keystore as ks_mod
    importlib.reload(ks_mod)
    ks_mod.init_keystore()
    assert (tmp_path / "keys" / "identity.pem").exists()
    assert (tmp_path / "keys" / "identity.pub.pem").exists()


def test_init_keystore_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_KEYSTORE_DIR", str(tmp_path / "keys"))
    import importlib
    import envault.keystore as ks_mod
    importlib.reload(ks_mod)
    ks_mod.init_keystore()
    first = (tmp_path / "keys" / "identity.pem").read_bytes()
    ks_mod.init_keystore()
    second = (tmp_path / "keys" / "identity.pem").read_bytes()
    assert first == second
