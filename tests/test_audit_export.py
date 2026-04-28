"""Tests for envault.env_audit_export and envault.commands_audit_export."""

from __future__ import annotations

import json
import os
import types

import pytest

from envault.audit import log_event
from envault.env_audit_export import (
    export_audit,
    export_audit_csv,
    export_audit_json,
    export_audit_text,
)
from envault.commands_audit_export import cmd_audit_export


@pytest.fixture()
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    d.mkdir()
    return str(d)


def _make_args(**kwargs):
    defaults = {"format": "text", "limit": None, "output": None}
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# Unit tests for env_audit_export
# ---------------------------------------------------------------------------

def test_export_text_empty_vault(vault_dir):
    result = export_audit_text(vault_dir)
    assert "No audit events found" in result


def test_export_json_empty_vault(vault_dir):
    result = export_audit_json(vault_dir)
    assert json.loads(result) == []


def test_export_csv_empty_vault(vault_dir):
    result = export_audit_csv(vault_dir)
    assert result == ""


def test_export_text_contains_action(vault_dir):
    log_event(vault_dir, "push", "v1")
    result = export_audit_text(vault_dir)
    assert "push" in result
    assert "v1" in result


def test_export_json_contains_action(vault_dir):
    log_event(vault_dir, "pull", "v2")
    events = json.loads(export_audit_json(vault_dir))
    assert any(e["action"] == "pull" for e in events)


def test_export_csv_has_header_and_row(vault_dir):
    log_event(vault_dir, "init", "setup")
    result = export_audit_csv(vault_dir)
    assert "timestamp" in result
    assert "action" in result
    assert "init" in result


def test_export_limit_restricts_rows(vault_dir):
    for i in range(5):
        log_event(vault_dir, f"event_{i}", f"detail_{i}")
    events = json.loads(export_audit_json(vault_dir, limit=2))
    assert len(events) == 2
    assert events[-1]["action"] == "event_4"


def test_export_unsupported_format_raises(vault_dir):
    with pytest.raises(ValueError, match="Unsupported format"):
        export_audit(vault_dir, fmt="xml")


# ---------------------------------------------------------------------------
# Integration tests for cmd_audit_export
# ---------------------------------------------------------------------------

def test_cmd_audit_export_stdout(vault_dir, capsys):
    log_event(vault_dir, "push", "v1")
    args = _make_args(vault_dir=vault_dir, format="text")
    cmd_audit_export(args)
    captured = capsys.readouterr()
    assert "push" in captured.out


def test_cmd_audit_export_json_stdout(vault_dir, capsys):
    log_event(vault_dir, "pull", "v3")
    args = _make_args(vault_dir=vault_dir, format="json")
    cmd_audit_export(args)
    captured = capsys.readouterr()
    events = json.loads(captured.out)
    assert isinstance(events, list)
    assert events[0]["action"] == "pull"


def test_cmd_audit_export_to_file(vault_dir, tmp_path, capsys):
    log_event(vault_dir, "init", "boot")
    out_file = str(tmp_path / "audit.txt")
    args = _make_args(vault_dir=vault_dir, format="text", output=out_file)
    cmd_audit_export(args)
    assert os.path.isfile(out_file)
    with open(out_file) as fh:
        content = fh.read()
    assert "init" in content
    captured = capsys.readouterr()
    assert "exported" in captured.out
