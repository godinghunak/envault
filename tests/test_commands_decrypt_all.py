"""Tests for commands_decrypt_all CLI commands."""

import pytest
import argparse
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_decrypt_all import cmd_decrypt_all, cmd_decrypt_version, cmd_decrypt_list


PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / "vault")
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("HELLO=world\nSECRET=abc\n")
    return str(f)


def make_args(vault_dir, password=PASSWORD, **kwargs):
    ns = argparse.Namespace(vault_dir=vault_dir, password=password, **kwargs)
    return ns


def push(vault_dir, env_file):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=PASSWORD)
    cmd_push(args)


def test_cmd_decrypt_all_empty(vault_dir, capsys):
    cmd_decrypt_all(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "No versions" in out


def test_cmd_decrypt_all_shows_content(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_decrypt_all(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "Version 1" in out
    assert "HELLO=world" in out


def test_cmd_decrypt_version_shows_content(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_decrypt_version(make_args(vault_dir, version=1))
    out = capsys.readouterr().out
    assert "HELLO=world" in out


def test_cmd_decrypt_list_shows_versions(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_decrypt_list(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "1" in out


def test_cmd_decrypt_list_wrong_password(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_decrypt_list(make_args(vault_dir, password="wrong"))
    out = capsys.readouterr().out
    assert "No decryptable" in out
