import pytest
from unittest.mock import patch
from types import SimpleNamespace
from envault.commands_placeholder import cmd_placeholder_check
from envault.vault import init_vault
from envault.commands import cmd_push
import tempfile, os


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / '.env'
    p.write_text('API_KEY=realvalue\nDB_PASS=secret\n')
    return str(p)


@pytest.fixture
def env_file_with_placeholder(tmp_path):
    p = tmp_path / '.env'
    p.write_text('API_KEY=<YOUR_API_KEY>\nDB_PASS=secret\n')
    return str(p)


def push(vault_dir, env_file, password='pass'):
    args = SimpleNamespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def make_args(vault_dir, password='pass', version=None):
    return SimpleNamespace(vault_dir=vault_dir, password=password, version=version)


def test_cmd_placeholder_check_no_versions(vault_dir, capsys):
    args = make_args(vault_dir)
    cmd_placeholder_check(args)
    out = capsys.readouterr().out
    assert 'No versions' in out


def test_cmd_placeholder_check_clean(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir)
    cmd_placeholder_check(args)
    out = capsys.readouterr().out
    assert 'No placeholders' in out


def test_cmd_placeholder_check_finds_placeholder(vault_dir, env_file_with_placeholder, capsys):
    push(vault_dir, env_file_with_placeholder)
    args = make_args(vault_dir)
    cmd_placeholder_check(args)
    out = capsys.readouterr().out
    assert 'API_KEY' in out


def test_cmd_placeholder_check_specific_version(vault_dir, env_file_with_placeholder, capsys):
    push(vault_dir, env_file_with_placeholder)
    args = make_args(vault_dir, version=1)
    cmd_placeholder_check(args)
    out = capsys.readouterr().out
    assert 'v1' in out
