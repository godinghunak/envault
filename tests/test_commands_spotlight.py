"""Tests for envault.commands_spotlight."""
from __future__ import annotations

import argparse
import pytest
from unittest.mock import patch

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_spotlight import cmd_spotlight


PASSWORD = "testpass"


@pytest.fixture()
def vault_dir(tmp_path):
    vd = str(tmp_path / "vault")
    init_vault(vd)
    return vd


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("API_KEY=secret\nDB_URL=postgres://localhost/db\n")
    return str(p)


def push(vault_dir, env_file):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=PASSWORD)
    cmd_push(args)


def make_args(vault_dir, keys):
    return argparse.Namespace(vault_dir=vault_dir, keys=keys)


def test_cmd_spotlight_prints_output(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir, ["API_KEY"])
    with patch("envault.commands_spotlight.getpass.getpass", return_value=PASSWORD):
        cmd_spotlight(args)
    captured = capsys.readouterr()
    assert "API_KEY" in captured.out


def test_cmd_spotlight_missing_key_shows_missing(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir, ["NONEXISTENT"])
    with patch("envault.commands_spotlight.getpass.getpass", return_value=PASSWORD):
        cmd_spotlight(args)
    captured = capsys.readouterr()
    assert "NONEXISTENT" in captured.out
    assert "<missing>" in captured.out


def test_cmd_spotlight_no_keys_exits(vault_dir, capsys):
    args = make_args(vault_dir, [])
    with patch("envault.commands_spotlight.getpass.getpass", return_value=PASSWORD):
        with pytest.raises(SystemExit):
            cmd_spotlight(args)


def test_cmd_spotlight_multiple_keys(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir, ["API_KEY", "DB_URL"])
    with patch("envault.commands_spotlight.getpass.getpass", return_value=PASSWORD):
        cmd_spotlight(args)
    captured = capsys.readouterr()
    assert "API_KEY" in captured.out
    assert "DB_URL" in captured.out
