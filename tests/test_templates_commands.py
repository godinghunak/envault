import pytest
import types
from pathlib import Path
from envault.vault import init_vault
from envault.templates import add_template
from envault.templates_commands import (
    cmd_template_add,
    cmd_template_remove,
    cmd_template_list,
    cmd_template_show,
)


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(tmp_path)
    return tmp_path


def make_args(vault_dir, **kwargs):
    args = types.SimpleNamespace(vault_dir=vault_dir, **kwargs)
    return args


def test_cmd_template_add(vault_dir, capsys):
    args = make_args(vault_dir, name="backend", keys="DB_URL,SECRET_KEY")
    cmd_template_add(args)
    out = capsys.readouterr().out
    assert "backend" in out
    assert "DB_URL" in out


def test_cmd_template_list_empty(vault_dir, capsys):
    args = make_args(vault_dir)
    cmd_template_list(args)
    out = capsys.readouterr().out
    assert "No templates" in out


def test_cmd_template_list_shows_templates(vault_dir, capsys):
    add_template(vault_dir, "frontend", ["API_URL", "PORT"])
    args = make_args(vault_dir)
    cmd_template_list(args)
    out = capsys.readouterr().out
    assert "frontend" in out
    assert "API_URL" in out


def test_cmd_template_remove(vault_dir, capsys):
    add_template(vault_dir, "temp", ["X"])
    args = make_args(vault_dir, name="temp")
    cmd_template_remove(args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_template_show_not_found(vault_dir, capsys):
    args = make_args(vault_dir, name="missing")
    cmd_template_show(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_template_show(vault_dir, capsys):
    add_template(vault_dir, "svc", ["HOST", "PORT"])
    args = make_args(vault_dir, name="svc")
    cmd_template_show(args)
    out = capsys.readouterr().out
    assert "HOST" in out
    assert "PORT" in out
