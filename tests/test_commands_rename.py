import pytest
import argparse
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_rename import cmd_rename, cmd_keys
from envault.diff import parse_env
from envault.export import export_latest

PASSWORD = 'testpass'


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / '.env'
    p.write_text('FOO=bar\nBAZ=qux\n')
    return str(p)


def make_args(**kwargs):
    defaults = dict(vault_dir=None, password=PASSWORD, version=None)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def push(vault_dir, env_file):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=PASSWORD)
    cmd_push(args)


def test_cmd_rename_prints_confirmation(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir=vault_dir, old_key='FOO', new_key='FOO_RENAMED')
    cmd_rename(args)
    out = capsys.readouterr().out
    assert 'FOO' in out
    assert 'FOO_RENAMED' in out
    assert 'version 2' in out


def test_cmd_rename_no_versions(vault_dir, capsys):
    args = make_args(vault_dir=vault_dir, old_key='FOO', new_key='BAR')
    cmd_rename(args)
    out = capsys.readouterr().out
    assert 'No versions' in out


def test_cmd_keys_lists_keys(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir=vault_dir)
    cmd_keys(args)
    out = capsys.readouterr().out
    assert 'FOO' in out
    assert 'BAZ' in out


def test_cmd_keys_no_versions(vault_dir, capsys):
    args = make_args(vault_dir=vault_dir)
    cmd_keys(args)
    out = capsys.readouterr().out
    assert 'No versions' in out
