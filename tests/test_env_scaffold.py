"""Tests for envault.env_scaffold."""
from __future__ import annotations

import pytest

from envault.env_scaffold import (
    ScaffoldError,
    scaffold_from_keys,
    scaffold_from_template,
    scaffold_to_file,
)


# ---------------------------------------------------------------------------
# scaffold_from_keys
# ---------------------------------------------------------------------------

def test_scaffold_from_keys_basic():
    result = scaffold_from_keys(["DB_HOST", "DB_PORT"])
    assert "DB_HOST=" in result
    assert "DB_PORT=" in result


def test_scaffold_from_keys_uppercases():
    result = scaffold_from_keys(["db_host"])
    assert "DB_HOST=" in result


def test_scaffold_from_keys_with_default():
    result = scaffold_from_keys(["API_KEY"], default_value="changeme")
    assert "API_KEY=changeme" in result


def test_scaffold_from_keys_empty_list():
    result = scaffold_from_keys([])
    assert result == ""


def test_scaffold_from_keys_invalid_key_raises():
    with pytest.raises(ScaffoldError):
        scaffold_from_keys(["INVALID KEY"])


def test_scaffold_from_keys_skips_blank_entries():
    result = scaffold_from_keys(["A", "", "B"])
    lines = [l for l in result.splitlines() if l]
    assert len(lines) == 2


# ---------------------------------------------------------------------------
# scaffold_from_template
# ---------------------------------------------------------------------------

def test_scaffold_from_template_passthrough():
    template = "DB_HOST=localhost\nDB_PORT=5432\n"
    result = scaffold_from_template(template)
    assert "DB_HOST=localhost" in result
    assert "DB_PORT=5432" in result


def test_scaffold_from_template_preserves_comments():
    template = "# Database settings\nDB_HOST=localhost\n"
    result = scaffold_from_template(template)
    assert "# Database settings" in result


def test_scaffold_from_template_preserves_blanks():
    template = "A=1\n\nB=2\n"
    result = scaffold_from_template(template)
    assert "\n\n" in result


def test_scaffold_from_template_invalid_line_raises():
    with pytest.raises(ScaffoldError):
        scaffold_from_template("NOT_A_VALID_LINE_WITHOUT_EQUALS")


# ---------------------------------------------------------------------------
# scaffold_to_file
# ---------------------------------------------------------------------------

def test_scaffold_to_file_writes_content(tmp_path):
    dest = tmp_path / ".env.scaffold"
    scaffold_to_file("A=1\n", dest)
    assert dest.read_text() == "A=1\n"


def test_scaffold_to_file_no_overwrite_raises(tmp_path):
    dest = tmp_path / ".env.scaffold"
    dest.write_text("existing")
    with pytest.raises(ScaffoldError):
        scaffold_to_file("A=1\n", dest, overwrite=False)


def test_scaffold_to_file_overwrite_replaces(tmp_path):
    dest = tmp_path / ".env.scaffold"
    dest.write_text("old")
    scaffold_to_file("A=1\n", dest, overwrite=True)
    assert dest.read_text() == "A=1\n"
