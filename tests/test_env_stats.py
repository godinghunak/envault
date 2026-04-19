"""Tests for envault.env_stats."""
import pytest
from pathlib import Path

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_stats import compute_stats, format_stats, VaultStats

PASSWORD = "statspass"


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("KEY1=val1\nKEY2=val2\n")
    return str(p)


def push(vault_dir, env_file, content=None):
    if content is not None:
        Path(env_file).write_text(content)
    import argparse
    args = argparse.Namespace(file=env_file, password=PASSWORD)
    cmd_push(args, vault_dir=vault_dir)


def test_stats_empty_vault(vault_dir):
    stats = compute_stats(vault_dir, PASSWORD)
    assert stats.total_versions == 0
    assert stats.unique_keys == 0
    assert stats.avg_keys_per_version == 0.0
    assert stats.most_changed_keys == []


def test_stats_single_version(vault_dir, env_file):
    push(vault_dir, env_file)
    stats = compute_stats(vault_dir, PASSWORD)
    assert stats.total_versions == 1
    assert stats.unique_keys == 2
    assert stats.key_frequency["KEY1"] == 1
    assert stats.key_frequency["KEY2"] == 1
    assert stats.avg_keys_per_version == 2.0


def test_stats_multiple_versions(vault_dir, env_file):
    push(vault_dir, env_file, "KEY1=a\nKEY2=b\n")
    push(vault_dir, env_file, "KEY1=c\nKEY3=d\n")
    stats = compute_stats(vault_dir, PASSWORD)
    assert stats.total_versions == 2
    assert "KEY1" in stats.key_frequency
    assert stats.key_frequency["KEY1"] == 2


def test_most_changed_keys_populated(vault_dir, env_file):
    push(vault_dir, env_file, "A=1\nB=2\n")
    push(vault_dir, env_file, "A=2\nB=2\n")
    push(vault_dir, env_file, "A=3\nB=3\n")
    stats = compute_stats(vault_dir, PASSWORD)
    assert "A" in stats.most_changed_keys


def test_format_stats_returns_string(vault_dir, env_file):
    push(vault_dir, env_file)
    stats = compute_stats(vault_dir, PASSWORD)
    output = format_stats(stats)
    assert "Total versions" in output
    assert "Unique keys" in output


def test_format_stats_empty_vault(vault_dir):
    stats = compute_stats(vault_dir, PASSWORD)
    output = format_stats(stats)
    assert "0" in output
