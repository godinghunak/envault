"""Tests for envault/commands_sign.py"""
import argparse
import pytest
from pathlib import Path

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_sign import cmd_sign, cmd_verify, cmd_sign_list


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\nSECRET=abc123\n")
    return str(f)


def push(vault_dir, env_file, password="pass"):
    a = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(a)


def make_args(vault_dir, **kwargs):
    return argparse.Namespace(vault_dir=vault_dir, **kwargs)


def test_cmd_sign_latest(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir, version=None, secret="s3cr3t")
    cmd_sign(args)
    out = capsys.readouterr().out
    assert "Signed version 1" in out


def test_cmd_sign_specific_version(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir, version=1, secret="s3cr3t")
    cmd_sign(args)
    out = capsys.readouterr().out
    assert "Signed version 1" in out


def test_cmd_verify_valid(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    sign_args = make_args(vault_dir, version=1, secret="s3cr3t")
    cmd_sign(sign_args)
    verify_args = make_args(vault_dir, version=1, secret="s3cr3t")
    cmd_verify(verify_args)
    out = capsys.readouterr().out
    assert "VALID" in out


def test_cmd_verify_invalid_secret(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_sign(make_args(vault_dir, version=1, secret="correct"))
    cmd_verify(make_args(vault_dir, version=1, secret="wrong"))
    out = capsys.readouterr().out
    assert "INVALID" in out


def test_cmd_verify_no_signature(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_verify(make_args(vault_dir, version=1, secret="s3cr3t"))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_sign_list_empty(vault_dir, capsys):
    cmd_sign_list(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "No signatures" in out


def test_cmd_sign_list_shows_entries(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_sign(make_args(vault_dir, version=1, secret="s3cr3t"))
    cmd_sign_list(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "v1" in out
