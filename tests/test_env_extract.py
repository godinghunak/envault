"""Tests for envault.env_extract."""

from __future__ import annotations

import os
import pytest

from envault.vault import init_vault, load_manifest
from envault.commands import cmd_push
from envault.env_extract import (
    ExtractionError,
    extract_keys,
    extract_to_file,
    extract_version,
)

PASSWORD = "testpass"


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\nDEBUG=true\n")
    return str(p)


def push(vault_dir, env_file):
    import argparse
    args = argparse.Namespace(
        vault_dir=vault_dir, env_file=env_file, password=PASSWORD
    )
    cmd_push(args)


# ── extract_keys unit tests ────────────────────────────────────────────────

def test_extract_keys_returns_subset():
    d = {"A": "1", "B": "2", "C": "3"}
    result = extract_keys(d, ["A", "C"])
    assert result == {"A": "1", "C": "3"}


def test_extract_keys_missing_raises():
    d = {"A": "1"}
    with pytest.raises(ExtractionError, match="Key not found"):
        extract_keys(d, ["A", "MISSING"])


def test_extract_keys_missing_ok_skips():
    d = {"A": "1"}
    result = extract_keys(d, ["A", "MISSING"], missing_ok=True)
    assert result == {"A": "1"}


def test_extract_keys_empty_keys_returns_empty():
    d = {"A": "1", "B": "2"}
    result = extract_keys(d, [])
    assert result == {}


# ── extract_version integration tests ─────────────────────────────────────

def test_extract_version_empty_vault_raises(vault_dir):
    with pytest.raises(ExtractionError, match="empty"):
        extract_version(vault_dir, PASSWORD, ["DB_HOST"])


def test_extract_version_creates_new_version(vault_dir, env_file):
    push(vault_dir, env_file)
    manifest_before = load_manifest(vault_dir)
    count_before = len(manifest_before["versions"])
    extract_version(vault_dir, PASSWORD, ["DB_HOST", "DB_PORT"])
    manifest_after = load_manifest(vault_dir)
    assert len(manifest_after["versions"]) == count_before + 1


def test_extract_version_content_correct(vault_dir, env_file):
    push(vault_dir, env_file)
    text = extract_version(vault_dir, PASSWORD, ["DB_HOST", "SECRET"])
    assert "DB_HOST=localhost" in text
    assert "SECRET=abc123" in text
    assert "DB_PORT" not in text


def test_extract_version_invalid_version_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(ExtractionError, match="not found"):
        extract_version(vault_dir, PASSWORD, ["DB_HOST"], version=999)


# ── extract_to_file integration tests ─────────────────────────────────────

def test_extract_to_file_writes_file(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    dest = str(tmp_path / "extracted.env")
    extract_to_file(vault_dir, PASSWORD, ["DEBUG"], dest)
    assert os.path.isfile(dest)
    content = open(dest).read()
    assert "DEBUG=true" in content


def test_extract_to_file_excludes_other_keys(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    dest = str(tmp_path / "extracted.env")
    extract_to_file(vault_dir, PASSWORD, ["DB_PORT"], dest)
    content = open(dest).read()
    assert "DB_HOST" not in content
    assert "SECRET" not in content
    assert "DB_PORT=5432" in content
