"""Tests for envault.commands_checksum."""

import argparse
import pytest
from pathlib import Path

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_checksum import (
    cmd_checksum_record,
    cmd_checksum_verify,
    cmd_checksum_show,
    cmd_checksum_list,
)

PASSWORD = "testpassword"


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(tmp_path)
    return tmp_path


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\nFOO=bar\n")
    return f


def push(vault_dir, env_file):
    args = argparse.Namespace(
        vault_dir=str(vault_dir),
        env_file=str(env_file),
        password=PASSWORD,
    )
    cmd_push(args)


def make_args(vault_dir, version=None, **kwargs):
    return argparse.Namespace(
        vault_dir=str(vault_dir),
        password=PASSWORD,
        version=version,
        **kwargs,
    )


def test_cmd_checksum_record_prints_checksum(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_checksum_record(make_args(vault_dir, version=1))
    out = capsys.readouterr().out
    assert "Recorded checksum for v1" in out


def test_cmd_checksum_record_uses_latest_when_no_version(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_checksum_record(make_args(vault_dir, version=None))
    out = capsys.readouterr().out
    assert "v1" in out


def test_cmd_checksum_verify_ok(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_checksum_record(make_args(vault_dir, version=1))
    capsys.readouterr()
    cmd_checksum_verify(make_args(vault_dir, version=1))
    out = capsys.readouterr().out
    assert "OK" in out


def test_cmd_checksum_verify_missing_entry(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_checksum_verify(make_args(vault_dir, version=1))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_checksum_show_no_entry(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_checksum_show(make_args(vault_dir, version=1))
    out = capsys.readouterr().out
    assert "No checksum" in out


def test_cmd_checksum_show_after_record(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_checksum_record(make_args(vault_dir, version=1))
    capsys.readouterr()
    cmd_checksum_show(make_args(vault_dir, version=1))
    out = capsys.readouterr().out
    assert "sha256" in out


def test_cmd_checksum_list_empty(vault_dir, capsys):
    cmd_checksum_list(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "No checksums" in out


def test_cmd_checksum_list_shows_entries(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_checksum_record(make_args(vault_dir, version=1))
    capsys.readouterr()
    cmd_checksum_list(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "v1" in out
