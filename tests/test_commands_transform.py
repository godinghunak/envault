"""Tests for envault.commands_transform."""
import argparse
import pytest

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_transform import cmd_transform, cmd_transform_list


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("db_host=Localhost\nAPI_KEY='secret'\nPORT=5432\n")
    return str(p)


def push(vault_dir, env_file, password="pw"):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def make_args(vault_dir, transforms, version=None, verbose=False):
    return argparse.Namespace(
        vault_dir=vault_dir,
        transforms=transforms,
        version=version,
        verbose=verbose,
    )


def test_cmd_transform_uppercase_keys(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir, ["uppercase_keys"])
    cmd_transform(args)
    out = capsys.readouterr().out
    assert "DB_HOST=" in out
    assert "API_KEY=" in out


def test_cmd_transform_strip_quotes(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir, ["strip_quotes"])
    cmd_transform(args)
    out = capsys.readouterr().out
    assert "API_KEY=secret" in out


def test_cmd_transform_multiple(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir, ["uppercase_keys", "strip_quotes"])
    cmd_transform(args)
    out = capsys.readouterr().out
    assert "DB_HOST=Localhost" in out
    assert "API_KEY=secret" in out


def test_cmd_transform_unknown_exits(vault_dir, env_file):
    push(vault_dir, env_file)
    args = make_args(vault_dir, ["does_not_exist"])
    with pytest.raises(SystemExit):
        cmd_transform(args)


def test_cmd_transform_no_transforms_exits(vault_dir, env_file):
    push(vault_dir, env_file)
    args = make_args(vault_dir, [])
    with pytest.raises(SystemExit):
        cmd_transform(args)


def test_cmd_transform_list_output(capsys):
    args = argparse.Namespace(vault_dir=None)
    cmd_transform_list(args)
    out = capsys.readouterr().out
    assert "uppercase_keys" in out
    assert "strip_quotes" in out
    assert "trim_whitespace" in out
