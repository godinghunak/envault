"""Tests for commands_audit module."""
import pytest
import types
from envault.audit import log_event
from envault.commands_audit import cmd_log, cmd_log_clear


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def make_args(vault_dir, limit=None):
    args = types.SimpleNamespace(vault_dir=vault_dir, limit=limit)
    return args


def test_cmd_log_empty(vault_dir, capsys):
    cmd_log(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "No audit events" in out


def test_cmd_log_shows_events(vault_dir, capsys):
    log_event("push", {"version": 1, "file": ".env"}, vault_dir)
    cmd_log(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "PUSH" in out
    assert "version=1" in out


def test_cmd_log_limit(vault_dir, capsys):
    for i in range(5):
        log_event("push", {"version": i}, vault_dir)
    cmd_log(make_args(vault_dir, limit=2))
    out = capsys.readouterr().out
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 2


def test_cmd_log_clear(vault_dir, capsys):
    log_event("push", {"version": 1}, vault_dir)
    cmd_log_clear(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "cleared" in out.lower()
    from envault.audit import read_events
    assert read_events(vault_dir) == []
