"""Tests for env_diff_summary.py."""
from __future__ import annotations

import os
import pytest

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_diff_summary import summarize_diff, format_diff_summary, DiffSummary


@pytest.fixture()
def vault_dir(tmp_path):
    d = str(tmp_path / ".envault")
    init_vault(d)
    return d


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=production\n")
    return str(p)


def push(vault_dir, env_file, content, password="secret"):
    """Helper: overwrite env_file with content and push."""
    with open(env_file, "w") as f:
        f.write(content)

    class Args:
        pass

    a = Args()
    a.vault_dir = vault_dir
    a.env_file = env_file
    a.password = password
    cmd_push(a)


def test_summarize_diff_added_key(vault_dir, env_file):
    push(vault_dir, env_file, "DB_HOST=localhost\n")
    push(vault_dir, env_file, "DB_HOST=localhost\nNEW_KEY=value\n")
    summary = summarize_diff(vault_dir, "1", "2", "secret")
    assert "NEW_KEY" in summary.added
    assert summary.removed == []
    assert summary.changed == []


def test_summarize_diff_removed_key(vault_dir, env_file):
    push(vault_dir, env_file, "DB_HOST=localhost\nOLD_KEY=old\n")
    push(vault_dir, env_file, "DB_HOST=localhost\n")
    summary = summarize_diff(vault_dir, "1", "2", "secret")
    assert "OLD_KEY" in summary.removed
    assert summary.added == []


def test_summarize_diff_changed_key(vault_dir, env_file):
    push(vault_dir, env_file, "DB_HOST=localhost\n")
    push(vault_dir, env_file, "DB_HOST=remotehost\n")
    summary = summarize_diff(vault_dir, "1", "2", "secret")
    assert "DB_HOST" in summary.changed


def test_summarize_diff_no_changes(vault_dir, env_file):
    push(vault_dir, env_file, "DB_HOST=localhost\n")
    push(vault_dir, env_file, "DB_HOST=localhost\n")
    summary = summarize_diff(vault_dir, "1", "2", "secret")
    assert not summary.has_changes
    assert summary.unchanged == 1


def test_summarize_diff_total_changes(vault_dir, env_file):
    push(vault_dir, env_file, "A=1\nB=2\n")
    push(vault_dir, env_file, "A=99\nC=3\n")
    summary = summarize_diff(vault_dir, "1", "2", "secret")
    assert summary.total_changes == 3  # A changed, B removed, C added


def test_format_diff_summary_contains_versions(vault_dir, env_file):
    push(vault_dir, env_file, "X=1\n")
    push(vault_dir, env_file, "X=2\n")
    summary = summarize_diff(vault_dir, "1", "2", "secret")
    text = format_diff_summary(summary)
    assert "v1" in text
    assert "v2" in text


def test_format_diff_summary_lists_added_keys(vault_dir, env_file):
    push(vault_dir, env_file, "X=1\n")
    push(vault_dir, env_file, "X=1\nY=2\n")
    summary = summarize_diff(vault_dir, "1", "2", "secret")
    text = format_diff_summary(summary)
    assert "Y" in text
