"""Tests for envault.commands_lock."""
import pytest
from argparse import Namespace
from envault.vault import init_vault
from envault.env_lock import write_lock
from envault.commands_lock import cmd_lock_write, cmd_lock_show, cmd_lock_verify

PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY1=val1\nKEY2=val2\n")
    return str(f)


def push(vault_dir, env_file):
    from envault.vault import add_version
    with open(env_file) as fh:
        content = fh.read()
    add_version(vault_dir, content, PASSWORD)


def make_args(vault_dir, **kwargs):
    return Namespace(vault_dir=vault_dir, **kwargs)


def test_cmd_lock_write_prints_info(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_lock_write(make_args(vault_dir, version=None))
    out = capsys.readouterr().out
    assert "Lock written" in out
    assert "version=1" in out


def test_cmd_lock_write_no_versions_prints_error(vault_dir, capsys):
    cmd_lock_write(make_args(vault_dir, version=None))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_lock_show_prints_details(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    write_lock(vault_dir)
    cmd_lock_show(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "Locked version" in out
    assert "Checksum" in out


def test_cmd_lock_show_missing_prints_error(vault_dir, capsys):
    cmd_lock_show(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_lock_verify_passes(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    write_lock(vault_dir)
    cmd_lock_verify(make_args(vault_dir, password=PASSWORD))
    out = capsys.readouterr().out
    assert "verified" in out
