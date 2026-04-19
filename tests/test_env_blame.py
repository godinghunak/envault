"""Tests for env_blame module."""
import os
import pytest

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_blame import blame, BlameLine

PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    vd = str(tmp_path / ".envault")
    init_vault(vd)
    return vd


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("KEY_A=alpha\nKEY_B=beta\n")
    return str(p)


def push(vault_dir, env_file, password=PASSWORD):
    import argparse
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def test_blame_empty_vault_returns_empty(vault_dir):
    result = blame(vault_dir, PASSWORD)
    assert result == []


def test_blame_returns_blame_lines(vault_dir, env_file):
    push(vault_dir, env_file)
    result = blame(vault_dir, PASSWORD)
    assert len(result) == 2
    keys = {b.key for b in result}
    assert "KEY_A" in keys
    assert "KEY_B" in keys


def test_blame_lines_have_version_1(vault_dir, env_file):
    push(vault_dir, env_file)
    result = blame(vault_dir, PASSWORD)
    for line in result:
        assert line.version == 1


def test_blame_new_key_attributed_to_later_version(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    env2 = tmp_path / ".env2"
    env2.write_text("KEY_A=alpha\nKEY_B=beta\nKEY_C=gamma\n")
    push(vault_dir, str(env2))
    result = blame(vault_dir, PASSWORD)
    blame_map = {b.key: b for b in result}
    assert blame_map["KEY_A"].version == 1
    assert blame_map["KEY_C"].version == 2


def test_blame_invalid_version_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(ValueError):
        blame(vault_dir, PASSWORD, version=99)


def test_blame_str_format(vault_dir, env_file):
    push(vault_dir, env_file)
    result = blame(vault_dir, PASSWORD)
    for line in result:
        s = str(line)
        assert "v1" in s
        assert line.key in s
