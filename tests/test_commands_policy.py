import types
import pytest
from envault.vault import init_vault
from envault.env_policy import set_rule
from envault.commands_policy import (
    cmd_policy_set, cmd_policy_remove, cmd_policy_show, cmd_policy_check
)
from envault.commands import cmd_push


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    return str(f)


def make_args(**kwargs):
    return types.SimpleNamespace(**kwargs)


def push(vault_dir, env_file, password="secret"):
    cmd_push(make_args(vault_dir=vault_dir, env_file=env_file, password=password))


def test_cmd_policy_set_prints_confirmation(vault_dir, capsys):
    args = make_args(vault_dir=vault_dir, name="max_keys", value="5")
    cmd_policy_set(args)
    out = capsys.readouterr().out
    assert "max_keys" in out


def test_cmd_policy_set_list_value(vault_dir, capsys):
    args = make_args(vault_dir=vault_dir, name="require_keys", value='["DB_HOST"]')
    cmd_policy_set(args)
    from envault.env_policy import load_policy
    assert load_policy(vault_dir)["require_keys"] == ["DB_HOST"]


def test_cmd_policy_remove_prints_confirmation(vault_dir, capsys):
    set_rule(vault_dir, "max_keys", 10)
    args = make_args(vault_dir=vault_dir, name="max_keys")
    cmd_policy_remove(args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_policy_remove_missing_prints_error(vault_dir, capsys):
    args = make_args(vault_dir=vault_dir, name="nonexistent")
    cmd_policy_remove(args)
    out = capsys.readouterr().out
    assert "not found" in out.lower() or "nonexistent" in out


def test_cmd_policy_show_empty(vault_dir, capsys):
    args = make_args(vault_dir=vault_dir)
    cmd_policy_show(args)
    out = capsys.readouterr().out
    assert "No policy" in out


def test_cmd_policy_show_with_rules(vault_dir, capsys):
    set_rule(vault_dir, "max_keys", 5)
    args = make_args(vault_dir=vault_dir)
    cmd_policy_show(args)
    out = capsys.readouterr().out
    assert "max_keys" in out


def test_cmd_policy_check_pass(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    set_rule(vault_dir, "require_keys", ["DB_HOST"])
    args = make_args(vault_dir=vault_dir, password="secret")
    cmd_policy_check(args)
    out = capsys.readouterr().out
    assert "passed" in out


def test_cmd_policy_check_fail(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    set_rule(vault_dir, "require_keys", ["MISSING_KEY"])
    args = make_args(vault_dir=vault_dir, password="secret")
    cmd_policy_check(args)
    out = capsys.readouterr().out
    assert "MISSING_KEY" in out
