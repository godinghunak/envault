"""Tests for envault.commands_resolve."""
import types
import pytest
from pathlib import Path

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_resolve import cmd_resolve


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("HOST=localhost\nPORT=5432\nURL=http://${HOST}:${PORT}\n")
    return str(p)


def push(vault_dir, env_file, password="secret"):
    args = types.SimpleNamespace(
        vault_dir=vault_dir, env_file=env_file, password=password, message=None
    )
    cmd_push(args)


def make_args(vault_dir, **kwargs):
    defaults = dict(vault_dir=vault_dir, version=None, overlay=None, strict=False)
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def test_cmd_resolve_latest_prints_keys(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_resolve(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "HOST=localhost" in out
    assert "PORT=5432" in out


def test_cmd_resolve_expands_references(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_resolve(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "URL=http://localhost:5432" in out


def test_cmd_resolve_specific_version(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_resolve(make_args(vault_dir, version=1))
    out = capsys.readouterr().out
    assert "HOST=localhost" in out


def test_cmd_resolve_missing_ref_exits_nonzero(vault_dir, tmp_path, capsys):
    bad = tmp_path / "bad.env"
    bad.write_text("URL=http://${UNDEFINED_HOST}\n")
    push(vault_dir, str(bad))
    with pytest.raises(SystemExit) as exc_info:
        cmd_resolve(make_args(vault_dir, strict=True))
    assert exc_info.value.code != 0


def test_cmd_resolve_overlay_overrides_base(vault_dir, tmp_path, capsys):
    base = tmp_path / "base.env"
    base.write_text("HOST=localhost\nURL=http://${HOST}\n")
    push(vault_dir, str(base))

    overlay = tmp_path / "overlay.env"
    overlay.write_text("HOST=production.example.com\n")
    push(vault_dir, str(overlay))

    cmd_resolve(make_args(vault_dir, version=1, overlay="2"))
    out = capsys.readouterr().out
    assert "URL=http://production.example.com" in out
