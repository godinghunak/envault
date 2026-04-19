import pytest
from types import SimpleNamespace
from envault.commands_access import (
    cmd_access_grant, cmd_access_revoke, cmd_access_list, cmd_access_check
)
from envault.env_access import grant


@pytest.fixture
def vault_dir(tmp_path):
    (tmp_path / ".envault").mkdir()
    return str(tmp_path)


def make_args(vault_dir, **kwargs):
    return SimpleNamespace(vault_dir=vault_dir, **kwargs)


def test_cmd_access_grant_prints_confirmation(vault_dir, capsys):
    args = make_args(vault_dir, role="dev", key="DB_HOST")
    cmd_access_grant(args)
    out = capsys.readouterr().out
    assert "dev" in out
    assert "DB_HOST" in out


def test_cmd_access_revoke_prints_confirmation(vault_dir, capsys):
    grant(vault_dir, "dev", "DB_HOST")
    args = make_args(vault_dir, role="dev", key="DB_HOST")
    cmd_access_revoke(args)
    out = capsys.readouterr().out
    assert "Revoked" in out


def test_cmd_access_list_empty(vault_dir, capsys):
    args = make_args(vault_dir, role="nobody")
    cmd_access_list(args)
    out = capsys.readouterr().out
    assert "No keys" in out


def test_cmd_access_list_shows_keys(vault_dir, capsys):
    grant(vault_dir, "dev", "API_KEY")
    grant(vault_dir, "dev", "DB_URL")
    args = make_args(vault_dir, role="dev")
    cmd_access_list(args)
    out = capsys.readouterr().out
    assert "API_KEY" in out
    assert "DB_URL" in out


def test_cmd_access_check_allowed(vault_dir, capsys):
    grant(vault_dir, "dev", "TOKEN")
    args = make_args(vault_dir, role="dev", key="TOKEN")
    cmd_access_check(args)
    out = capsys.readouterr().out
    assert "ALLOWED" in out


def test_cmd_access_check_denied(vault_dir, capsys):
    args = make_args(vault_dir, role="guest", key="TOKEN")
    cmd_access_check(args)
    out = capsys.readouterr().out
    assert "DENIED" in out
