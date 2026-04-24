"""Tests for envault.commands_report."""

from __future__ import annotations

import argparse
import pytest

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_report import cmd_report, register


PASSWORD = "cmdreportpass"


@pytest.fixture()
def vault_dir(tmp_path):
    d = str(tmp_path / ".envault")
    init_vault(d)
    return d


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("APP_NAME=envault\nAPP_ENV=test\n")
    return str(p)


def make_args(vault_dir, **kwargs):
    defaults = dict(vault_dir=vault_dir, password=PASSWORD, limit=5)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def push(vault_dir, env_file):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=PASSWORD)
    cmd_push(args)


def test_cmd_report_empty_vault(vault_dir, capsys):
    cmd_report(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "Summary" in out
    assert "Health" in out


def test_cmd_report_after_push(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_report(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "Total versions" in out
    assert "Latest version" in out


def test_cmd_report_shows_health_ok(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_report(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "Health" in out


def test_cmd_report_limit_option(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_report(make_args(vault_dir, limit=1))
    out = capsys.readouterr().out
    assert "Recent Activity" in out


def test_register_adds_report_subcommand():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register(subparsers)
    args = parser.parse_args(["report", "--password", "secret"])
    assert hasattr(args, "func")
    assert args.password == "secret"
    assert args.limit == 5
