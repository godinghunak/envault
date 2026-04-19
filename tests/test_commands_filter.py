"""Tests for envault.commands_filter."""
import argparse
import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_filter import cmd_filter


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_SECRET=xyz\nAPP_DEBUG=true\n")
    return str(p)


def push(vault_dir, env_file, password="pw"):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def make_args(vault_dir, **kwargs):
    defaults = dict(vault_dir=vault_dir, password="pw", pattern="*", prefix=None, version=None, output=None)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_filter_all_keys(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_filter(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "DB_HOST=localhost" in out
    assert "APP_SECRET=xyz" in out


def test_cmd_filter_by_pattern(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_filter(make_args(vault_dir, pattern="DB_*"))
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "APP_SECRET" not in out


def test_cmd_filter_by_prefix(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_filter(make_args(vault_dir, prefix="APP_"))
    out = capsys.readouterr().out
    assert "APP_DEBUG" in out
    assert "DB_HOST" not in out


def test_cmd_filter_no_match(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_filter(make_args(vault_dir, pattern="NOPE_*"))
    out = capsys.readouterr().out
    assert "No keys matched" in out


def test_cmd_filter_writes_output_file(vault_dir, env_file, tmp_path, capsys):
    push(vault_dir, env_file)
    out_file = str(tmp_path / "filtered.env")
    cmd_filter(make_args(vault_dir, pattern="DB_*", output=out_file))
    content = Path(out_file).read_text()
    assert "DB_HOST=localhost" in content
    assert "APP_SECRET" not in content
