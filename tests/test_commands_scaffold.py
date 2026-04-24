"""Tests for envault.commands_scaffold."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

from envault.commands_scaffold import cmd_scaffold, register


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def make_args(**kwargs):
    defaults = dict(keys=None, template=None, output=None, default="", overwrite=False)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_cmd_scaffold_from_keys(tmp_path, capsys):
    dest = tmp_path / "out.env"
    args = make_args(keys=["DB_HOST", "DB_PORT"], output=str(dest))
    cmd_scaffold(args)
    captured = capsys.readouterr()
    assert "Scaffold written to" in captured.out
    content = dest.read_text()
    assert "DB_HOST=" in content
    assert "DB_PORT=" in content


def test_cmd_scaffold_from_template(tmp_path, capsys):
    template = tmp_path / "template.env"
    template.write_text("API_KEY=<your-key>\n")
    dest = tmp_path / "out.env"
    args = make_args(template=str(template), output=str(dest))
    cmd_scaffold(args)
    content = dest.read_text()
    assert "API_KEY=<your-key>" in content


def test_cmd_scaffold_missing_template_exits(tmp_path):
    dest = tmp_path / "out.env"
    args = make_args(template="/nonexistent/file.env", output=str(dest))
    with pytest.raises(SystemExit):
        cmd_scaffold(args)


def test_cmd_scaffold_no_source_exits(tmp_path):
    dest = tmp_path / "out.env"
    args = make_args(output=str(dest))
    with pytest.raises(SystemExit):
        cmd_scaffold(args)


def test_cmd_scaffold_overwrite_flag(tmp_path, capsys):
    dest = tmp_path / "out.env"
    dest.write_text("old")
    args = make_args(keys=["X"], output=str(dest), overwrite=True)
    cmd_scaffold(args)
    assert "X=" in dest.read_text()


def test_cmd_scaffold_no_overwrite_exits(tmp_path):
    dest = tmp_path / "out.env"
    dest.write_text("old")
    args = make_args(keys=["X"], output=str(dest), overwrite=False)
    with pytest.raises(SystemExit):
        cmd_scaffold(args)


def test_register_adds_scaffold_subparser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register(subparsers)
    parsed = parser.parse_args(["scaffold", "--keys", "A", "B"])
    assert parsed.keys == ["A", "B"]
