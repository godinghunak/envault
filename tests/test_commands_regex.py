"""Tests for envault.commands_regex."""
import pytest
from unittest.mock import patch
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_regex import cmd_regex_keys, cmd_regex_values, cmd_regex_validate


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPI_KEY=abc123\nAPP_DEBUG=true\n")
    return str(p)


def push(vault_dir, env_file, password="secret"):
    class A:
        pass
    a = A()
    a.vault_dir = vault_dir
    a.env_file = env_file
    a.password = password
    cmd_push(a)


def make_args(vault_dir, **kwargs):
    class A:
        pass
    a = A()
    a.vault_dir = vault_dir
    a.version = None
    for k, v in kwargs.items():
        setattr(a, k, v)
    return a


def test_cmd_regex_keys_prints_matches(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    with patch("envault.commands_regex.export_latest", return_value="DB_HOST=localhost\nDB_PORT=5432\n"):
        args = make_args(vault_dir, pattern=r"^DB_")
        cmd_regex_keys(args)
    out = capsys.readouterr().out
    assert "DB_HOST" in out or "DB_PORT" in out


def test_cmd_regex_values_prints_matches(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    with patch("envault.commands_regex.export_latest", return_value="DB_PORT=5432\nAPI_KEY=abc123\n"):
        args = make_args(vault_dir, pattern=r"^\d+$")
        cmd_regex_values(args)
    out = capsys.readouterr().out
    assert "DB_PORT" in out


def test_cmd_regex_validate_passes(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    with patch("envault.commands_regex.export_latest", return_value="DB_PORT=5432\n"):
        args = make_args(vault_dir, rules=["DB_PORT=\\d+"])
        cmd_regex_validate(args)
    out = capsys.readouterr().out
    assert "DB_PORT" in out


def test_cmd_regex_validate_bad_rule_exits(vault_dir, env_file):
    push(vault_dir, env_file)
    with patch("envault.commands_regex.export_latest", return_value="DB_PORT=5432\n"):
        args = make_args(vault_dir, rules=["NORULE"])
        with pytest.raises(SystemExit):
            cmd_regex_validate(args)


def test_cmd_regex_keys_invalid_pattern_exits(vault_dir, env_file):
    push(vault_dir, env_file)
    with patch("envault.commands_regex.export_latest", return_value="DB_HOST=localhost\n"):
        args = make_args(vault_dir, pattern=r"[invalid")
        with pytest.raises(SystemExit):
            cmd_regex_keys(args)
