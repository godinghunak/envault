import argparse
import pytest
from pathlib import Path

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_mask import cmd_mask


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    init_vault(str(d))
    return str(d)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("APP_NAME=myapp\nDB_PASSWORD=supersecret\nAPI_KEY=key123\n")
    return str(f)


def push(vault_dir, env_file, password="pass"):
    args = argparse.Namespace(
        vault_dir=vault_dir, env_file=env_file, password=password
    )
    cmd_push(args)


def make_args(vault_dir, password="pass", version=None, show_chars=0):
    return argparse.Namespace(
        vault_dir=vault_dir,
        password=password,
        version=version,
        show_chars=show_chars,
    )


def test_cmd_mask_hides_sensitive(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_mask(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "APP_NAME=myapp" in out
    assert "supersecret" not in out
    assert "DB_PASSWORD=****" in out


def test_cmd_mask_show_chars(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_mask(make_args(vault_dir, show_chars=3))
    out = capsys.readouterr().out
    assert "ret" in out  # last 3 chars of 'supersecret'


def test_cmd_mask_no_versions_exits(vault_dir, capsys):
    args = make_args(vault_dir)
    with pytest.raises(SystemExit):
        cmd_mask(args)


def test_cmd_mask_invalid_version_exits(vault_dir, env_file):
    push(vault_dir, env_file)
    args = make_args(vault_dir, version="v99")
    with pytest.raises(SystemExit):
        cmd_mask(args)
