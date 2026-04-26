"""Tests for env_changelog module."""

import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_changelog import (
    build_changelog,
    format_changelog,
    ChangelogEntry,
)


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / ".envault")
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    return tmp_path / ".env"


def push(vault_dir, env_file, content, password="secret"):
    env_file.write_text(content)

    class Args:
        pass

    a = Args()
    a.vault_dir = vault_dir
    a.file = str(env_file)
    a.password = password
    cmd_push(a)


def test_changelog_empty_vault(vault_dir):
    entries = build_changelog(vault_dir, "secret")
    assert entries == []


def test_changelog_single_version_returns_empty(vault_dir, env_file):
    push(vault_dir, env_file, "KEY=value\n")
    entries = build_changelog(vault_dir, "secret")
    assert entries == []


def test_changelog_two_versions_detects_added(vault_dir, env_file):
    push(vault_dir, env_file, "KEY=value\n")
    push(vault_dir, env_file, "KEY=value\nNEW_KEY=hello\n")
    entries = build_changelog(vault_dir, "secret")
    assert len(entries) == 1
    assert "NEW_KEY" in entries[0].added
    assert entries[0].version == 2


def test_changelog_detects_removed(vault_dir, env_file):
    push(vault_dir, env_file, "KEY=value\nOLD=bye\n")
    push(vault_dir, env_file, "KEY=value\n")
    entries = build_changelog(vault_dir, "secret")
    assert len(entries) == 1
    assert "OLD" in entries[0].removed


def test_changelog_detects_modified(vault_dir, env_file):
    push(vault_dir, env_file, "KEY=original\n")
    push(vault_dir, env_file, "KEY=changed\n")
    entries = build_changelog(vault_dir, "secret")
    assert len(entries) == 1
    assert "KEY" in entries[0].modified


def test_changelog_from_to_range(vault_dir, env_file):
    push(vault_dir, env_file, "A=1\n")
    push(vault_dir, env_file, "A=1\nB=2\n")
    push(vault_dir, env_file, "A=1\nB=2\nC=3\n")
    entries = build_changelog(vault_dir, "secret", from_version=2, to_version=3)
    assert len(entries) == 1
    assert entries[0].version == 3
    assert "C" in entries[0].added


def test_format_changelog_no_entries():
    result = format_changelog([])
    assert "No changelog" in result


def test_changelog_entry_str_no_changes():
    entry = ChangelogEntry(version=1)
    assert "no changes" in str(entry)


def test_changelog_entry_has_changes_false():
    entry = ChangelogEntry(version=1)
    assert not entry.has_changes()


def test_changelog_entry_has_changes_true():
    entry = ChangelogEntry(version=2, added=["FOO"])
    assert entry.has_changes()
