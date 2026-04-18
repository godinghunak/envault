import pytest
import os
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_compare import (
    compare_dicts,
    compare_versions,
    compare_file_to_version,
    format_compare,
)
import argparse


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / ".envault")
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    return str(tmp_path / ".env")


def push(vault_dir, env_file, content, password="secret"):
    with open(env_file, "w") as f:
        f.write(content)
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def test_compare_dicts_identical():
    a = {"A": "1", "B": "2"}
    result = compare_dicts(a, dict(a))
    assert not result.has_differences()
    assert result.same_value == ["A", "B"]


def test_compare_dicts_only_in_a():
    result = compare_dicts({"X": "1"}, {})
    assert result.only_in_a == ["X"]
    assert result.only_in_b == []


def test_compare_dicts_different_value():
    result = compare_dicts({"K": "old"}, {"K": "new"})
    assert result.different_value == ["K"]
    assert result.has_differences()


def test_compare_versions(vault_dir, env_file):
    push(vault_dir, env_file, "A=1\nB=2\n")
    push(vault_dir, env_file, "A=1\nB=changed\nC=3\n")
    result = compare_versions(vault_dir, "secret", 1, 2)
    assert "B" in result.different_value
    assert "C" in result.only_in_b
    assert "A" in result.same_value


def test_compare_file_to_latest(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file, "A=1\nB=2\n")
    local = str(tmp_path / "local.env")
    with open(local, "w") as f:
        f.write("A=1\nC=99\n")
    result = compare_file_to_version(vault_dir, "secret", local)
    assert "C" in result.only_in_a
    assert "B" in result.only_in_b


def test_format_compare_no_diff():
    from envault.env_compare import CompareResult
    r = CompareResult(same_value=["X"])
    out = format_compare(r, "v1", "v2")
    assert "match" in out
    assert "X" in out


def test_format_compare_with_conflict():
    from envault.env_compare import CompareResult
    r = CompareResult(different_value=["SECRET"])
    out = format_compare(r)
    assert "conflict" in out
    assert "SECRET" in out
