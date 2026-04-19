"""Tests for envault/env_prune.py"""

import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_prune import prune_versions, prune_preview
import argparse


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / ".envault")
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return str(f)


def push(vault_dir, env_file, password="secret", n=1):
    for _ in range(n):
        args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
        cmd_push(args)


def test_prune_empty_vault_returns_empty(vault_dir):
    result = prune_versions(vault_dir, password="secret", keep=5)
    assert result == []


def test_prune_fewer_than_keep_returns_empty(vault_dir, env_file):
    push(vault_dir, env_file, n=3)
    result = prune_versions(vault_dir, password="secret", keep=5)
    assert result == []


def test_prune_removes_old_versions(vault_dir, env_file):
    push(vault_dir, env_file, n=7)
    pruned = prune_versions(vault_dir, password="secret", keep=3)
    assert len(pruned) == 4
    assert pruned == [1, 2, 3, 4]


def test_prune_deletes_enc_files(vault_dir, env_file):
    push(vault_dir, env_file, n=5)
    prune_versions(vault_dir, password="secret", keep=2)
    vault_path = Path(vault_dir) / "vault"
    remaining = list(vault_path.glob("*.enc"))
    assert len(remaining) == 2


def test_prune_updates_manifest(vault_dir, env_file):
    from envault.vault import load_manifest
    push(vault_dir, env_file, n=5)
    prune_versions(vault_dir, password="secret", keep=2)
    manifest = load_manifest(vault_dir)
    assert manifest["versions"] == [4, 5]


def test_prune_preview_no_changes(vault_dir, env_file):
    push(vault_dir, env_file, n=3)
    result = prune_preview(vault_dir, keep=5)
    assert result["to_prune"] == []
    assert result["to_keep"] == [1, 2, 3]


def test_prune_preview_shows_correct_split(vault_dir, env_file):
    push(vault_dir, env_file, n=6)
    result = prune_preview(vault_dir, keep=2)
    assert result["to_prune"] == [1, 2, 3, 4]
    assert result["to_keep"] == [5, 6]


def test_prune_invalid_keep_raises(vault_dir):
    with pytest.raises(ValueError):
        prune_versions(vault_dir, password="secret", keep=0)
