"""Tests for env merge feature."""
import pytest
from envault.env_merge import merge_dicts, MergeResult, MergeConflict, format_merged
from envault.vault import init_vault
from envault.commands import cmd_push
import argparse
import os


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / "vault"
    init_vault(str(d))
    return str(d)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("A=1\nB=2\nC=3\n")
    return str(f)


def push(vault_dir, env_file, content, password="pw"):
    env_file_path = env_file
    with open(env_file_path, "w") as f:
        f.write(content)
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file_path, password=password)
    cmd_push(args)


def test_merge_dicts_no_conflict():
    base = {"A": "1", "B": "2"}
    ours = {"A": "1", "B": "3"}  # ours changed B
    theirs = {"A": "10", "B": "2"}  # theirs changed A
    result = merge_dicts(base, ours, theirs)
    assert not result.has_conflicts
    assert result.merged["A"] == "10"
    assert result.merged["B"] == "3"


def test_merge_dicts_conflict():
    base = {"A": "1"}
    ours = {"A": "2"}
    theirs = {"A": "3"}
    result = merge_dicts(base, ours, theirs)
    assert result.has_conflicts
    assert len(result.conflicts) == 1
    assert result.conflicts[0].key == "A"
    assert result.merged["A"] == "2"  # ours kept


def test_merge_dicts_added_by_theirs():
    base = {"A": "1"}
    ours = {"A": "1"}
    theirs = {"A": "1", "B": "new"}
    result = merge_dicts(base, ours, theirs)
    assert not result.has_conflicts
    assert result.merged.get("B") == "new"


def test_merge_dicts_deleted_by_theirs():
    base = {"A": "1", "B": "2"}
    ours = {"A": "1", "B": "2"}
    theirs = {"A": "1"}
    result = merge_dicts(base, ours, theirs)
    assert not result.has_conflicts
    assert "B" not in result.merged


def test_merge_dicts_both_same_change():
    base = {"A": "1"}
    ours = {"A": "2"}
    theirs = {"A": "2"}
    result = merge_dicts(base, ours, theirs)
    assert not result.has_conflicts
    assert result.merged["A"] == "2"


def test_format_merged():
    merged = {"B": "2", "A": "1"}
    output = format_merged(merged)
    lines = output.strip().splitlines()
    assert lines[0] == "A=1"
    assert lines[1] == "B=2"


def test_merge_conflict_str():
    c = MergeConflict(key="X", base_value="old", theirs_value="new")
    s = str(c)
    assert "X" in s
    assert "old" in s
    assert "new" in s
