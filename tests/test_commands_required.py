"""Tests for envault.commands_required."""

import argparse
from pathlib import Path

import pytest

from envault.commands_required import cmd_required_check, cmd_required_list
from envault.commands import cmd_init, cmd_push


@pytest.fixture()
def vault_dir(tmp_path):
    d = tmp_path / "vault"
    d.mkdir()
    args = argparse.Namespace(vault_dir=str(d))
    cmd_init(args)
    return str(d)


@pytest.fixture()
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n")
    return str(f)


@pytest.fixture()
def required_file(tmp_path):
    f = tmp_path / ".env.required"
    f.write_text("DB_HOST\nDB_PORT\nSECRET_KEY\n")
    return str(f)


def push(vault_dir, env_file, password="pass"):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def make_args(**kwargs):
    base = {"vault_dir": None, "password": "pass", "file": None, "version": None}
    base.update(kwargs)
    return argparse.Namespace(**base)


def test_cmd_required_check_all_present(vault_dir, env_file, required_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir=vault_dir, required_file=required_file)
    cmd_required_check(args)
    out = capsys.readouterr().out
    assert "present" in out


def test_cmd_required_check_missing_exits(vault_dir, env_file, tmp_path, capsys):
    push(vault_dir, env_file)
    req = tmp_path / "strict.required"
    req.write_text("DB_HOST\nMISSING_KEY\n")
    args = make_args(vault_dir=vault_dir, required_file=str(req))
    with pytest.raises(SystemExit) as exc_info:
        cmd_required_check(args)
    assert exc_info.value.code == 1


def test_cmd_required_check_file_not_found(vault_dir, capsys):
    args = make_args(vault_dir=vault_dir, required_file="/nonexistent/.env.required")
    cmd_required_check(args)  # should not raise
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_required_check_local_file(vault_dir, env_file, required_file, capsys):
    args = make_args(vault_dir=vault_dir, required_file=required_file, file=env_file)
    cmd_required_check(args)
    out = capsys.readouterr().out
    assert "present" in out


def test_cmd_required_list_shows_keys(required_file, capsys):
    args = make_args(required_file=required_file)
    cmd_required_list(args)
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "SECRET_KEY" in out


def test_cmd_required_list_empty(tmp_path, capsys):
    req = tmp_path / "empty.required"
    req.write_text("# just a comment\n")
    args = make_args(required_file=str(req))
    cmd_required_list(args)
    out = capsys.readouterr().out
    assert "No required keys" in out
