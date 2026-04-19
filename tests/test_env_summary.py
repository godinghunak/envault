"""Tests for env_summary module."""
import os
import pytest

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.tags import add_tag
from envault.profiles import add_profile
from envault.env_summary import summarize, format_summary


PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / ".envault")
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n")
    return str(f)


def push(vault_dir, env_file):
    import argparse
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=PASSWORD)
    cmd_push(args)


def test_summary_empty_vault(vault_dir):
    s = summarize(vault_dir, PASSWORD)
    assert s.total_versions == 0
    assert s.latest_version == 0
    assert s.total_keys == 0
    assert s.key_names == []
    assert s.tags == {}
    assert s.profiles == []


def test_summary_after_push(vault_dir, env_file):
    push(vault_dir, env_file)
    s = summarize(vault_dir, PASSWORD)
    assert s.total_versions == 1
    assert s.latest_version == 1
    assert s.total_keys == 3
    assert "DB_HOST" in s.key_names
    assert "SECRET_KEY" in s.key_names


def test_summary_includes_tags(vault_dir, env_file):
    push(vault_dir, env_file)
    add_tag(vault_dir, "stable", 1)
    s = summarize(vault_dir, PASSWORD)
    assert "stable" in s.tags
    assert s.tags["stable"] == 1


def test_summary_includes_profiles(vault_dir, env_file):
    push(vault_dir, env_file)
    add_profile(vault_dir, "production", {"DB_HOST": "prod-host"})
    s = summarize(vault_dir, PASSWORD)
    assert "production" in s.profiles


def test_format_summary_contains_versions(vault_dir, env_file):
    push(vault_dir, env_file)
    s = summarize(vault_dir, PASSWORD)
    out = format_summary(s)
    assert "Versions" in out
    assert "1" in out


def test_format_summary_no_tags_label(vault_dir):
    s = summarize(vault_dir, PASSWORD)
    out = format_summary(s)
    assert "(none)" in out
