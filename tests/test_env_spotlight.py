"""Tests for envault.env_spotlight."""
from __future__ import annotations

import os
import pytest

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_spotlight import (
    spotlight_key,
    spotlight_keys,
    format_spotlight,
    SpotlightResult,
    SpotlightEntry,
)


PASSWORD = "testpass"


@pytest.fixture()
def vault_dir(tmp_path):
    vd = str(tmp_path / "vault")
    init_vault(vd)
    return vd


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    return str(p)


def push(vault_dir, env_file, content):
    import argparse
    with open(env_file, "w") as f:
        f.write(content)
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=PASSWORD)
    cmd_push(args)


def test_spotlight_key_empty_vault(vault_dir):
    result = spotlight_key(vault_dir, "DB_HOST", PASSWORD)
    assert isinstance(result, SpotlightResult)
    assert result.key == "DB_HOST"
    assert result.entries == []


def test_spotlight_key_present(vault_dir, env_file):
    push(vault_dir, env_file, "DB_HOST=localhost\n")
    result = spotlight_key(vault_dir, "DB_HOST", PASSWORD)
    assert len(result.entries) == 1
    assert result.entries[0].value == "localhost"
    assert result.entries[0].version == 1


def test_spotlight_key_missing_in_version(vault_dir, env_file):
    push(vault_dir, env_file, "DB_HOST=localhost\n")
    push(vault_dir, env_file, "OTHER=value\n")
    result = spotlight_key(vault_dir, "DB_HOST", PASSWORD)
    assert result.entries[0].value == "localhost"
    assert result.entries[1].value is None
    assert result.versions_missing == [2]


def test_spotlight_key_change_detected(vault_dir, env_file):
    push(vault_dir, env_file, "DB_HOST=localhost\n")
    push(vault_dir, env_file, "DB_HOST=remotehost\n")
    result = spotlight_key(vault_dir, "DB_HOST", PASSWORD)
    assert result.entries[0].changed is False
    assert result.entries[1].changed is True


def test_spotlight_unique_values(vault_dir, env_file):
    push(vault_dir, env_file, "DB_HOST=a\n")
    push(vault_dir, env_file, "DB_HOST=b\n")
    push(vault_dir, env_file, "DB_HOST=a\n")
    result = spotlight_key(vault_dir, "DB_HOST", PASSWORD)
    assert set(result.unique_values) == {"a", "b"}


def test_spotlight_keys_multiple(vault_dir, env_file):
    push(vault_dir, env_file, "A=1\nB=2\n")
    results = spotlight_keys(vault_dir, ["A", "B"], PASSWORD)
    assert "A" in results
    assert "B" in results
    assert results["A"].entries[0].value == "1"
    assert results["B"].entries[0].value == "2"


def test_format_spotlight_contains_key(vault_dir, env_file):
    push(vault_dir, env_file, "MY_KEY=hello\n")
    result = spotlight_key(vault_dir, "MY_KEY", PASSWORD)
    output = format_spotlight(result)
    assert "MY_KEY" in output
    assert "hello" in output


def test_format_spotlight_empty(vault_dir):
    result = spotlight_key(vault_dir, "GHOST", PASSWORD)
    output = format_spotlight(result)
    assert "No versions found" in output
