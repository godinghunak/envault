import pytest
import types
from envault.vault import init_vault
from envault.commands_profiles import (
    cmd_profile_add, cmd_profile_remove, cmd_profile_list, cmd_profile_show
)


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d)
    return d


def make_args(vault_dir, **kwargs):
    args = types.SimpleNamespace(vault_dir=vault_dir)
    for k, v in kwargs.items():
        setattr(args, k, v)
    return args


def test_cmd_profile_add(vault_dir, capsys):
    args = make_args(vault_dir, name="dev", env_file=".env.dev")
    cmd_profile_add(args)
    out = capsys.readouterr().out
    assert "dev" in out


def test_cmd_profile_list_empty(vault_dir, capsys):
    args = make_args(vault_dir)
    cmd_profile_list(args)
    out = capsys.readouterr().out
    assert "No profiles" in out


def test_cmd_profile_list_shows_profiles(vault_dir, capsys):
    cmd_profile_add(make_args(vault_dir, name="prod", env_file=".env.prod"))
    cmd_profile_list(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "prod" in out


def test_cmd_profile_remove(vault_dir, capsys):
    cmd_profile_add(make_args(vault_dir, name="dev", env_file=".env.dev"))
    cmd_profile_remove(make_args(vault_dir, name="dev"))
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_profile_remove_missing(vault_dir, capsys):
    cmd_profile_remove(make_args(vault_dir, name="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_profile_show(vault_dir, capsys):
    cmd_profile_add(make_args(vault_dir, name="staging", env_file=".env.staging"))
    cmd_profile_show(make_args(vault_dir, name="staging"))
    out = capsys.readouterr().out
    assert "staging" in out
    assert ".env.staging" in out
