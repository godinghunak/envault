"""Tests for envault.env_drift."""
import pytest

from envault.env_drift import (
    DriftEntry,
    DriftResult,
    detect_drift,
    detect_drift_from_text,
    format_drift,
)


def test_no_drift_identical_dicts():
    env = {"A": "1", "B": "2"}
    result = detect_drift(env, env.copy())
    assert not result.has_drift
    assert result.entries == []


def test_drift_added_key():
    vault = {"A": "1"}
    file = {"A": "1", "B": "new"}
    result = detect_drift(vault, file)
    assert result.has_drift
    assert len(result.by_kind("added")) == 1
    assert result.entries[0].key == "B"
    assert result.entries[0].file_value == "new"


def test_drift_removed_key():
    vault = {"A": "1", "B": "old"}
    file = {"A": "1"}
    result = detect_drift(vault, file)
    assert result.has_drift
    removed = result.by_kind("removed")
    assert len(removed) == 1
    assert removed[0].key == "B"
    assert removed[0].vault_value == "old"


def test_drift_changed_value():
    vault = {"A": "old"}
    file = {"A": "new"}
    result = detect_drift(vault, file)
    assert result.has_drift
    changed = result.by_kind("changed")
    assert len(changed) == 1
    assert changed[0].vault_value == "old"
    assert changed[0].file_value == "new"


def test_drift_multiple_kinds():
    vault = {"A": "1", "B": "2", "C": "3"}
    file = {"A": "changed", "C": "3", "D": "added"}
    result = detect_drift(vault, file)
    assert len(result.by_kind("added")) == 1
    assert len(result.by_kind("removed")) == 1
    assert len(result.by_kind("changed")) == 1


def test_detect_drift_from_text():
    vault_text = "A=1\nB=2\n"
    file_text = "A=1\nC=3\n"
    result = detect_drift_from_text(vault_text, file_text)
    assert result.has_drift
    assert any(e.key == "B" for e in result.by_kind("removed"))
    assert any(e.key == "C" for e in result.by_kind("added"))


def test_format_drift_no_drift():
    result = DriftResult()
    output = format_drift(result)
    assert "No drift" in output


def test_format_drift_shows_summary():
    vault = {"A": "1", "B": "2"}
    file = {"A": "changed", "C": "new"}
    result = detect_drift(vault, file)
    output = format_drift(result)
    assert "Summary" in output
    assert "1 added" in output
    assert "1 removed" in output


def test_drift_entry_str_added():
    e = DriftEntry("FOO", "added", file_value="bar")
    assert "+" in str(e)
    assert "FOO" in str(e)


def test_drift_entry_str_removed():
    e = DriftEntry("FOO", "removed", vault_value="bar")
    assert "-" in str(e)


def test_drift_entry_str_changed():
    e = DriftEntry("FOO", "changed", vault_value="old", file_value="new")
    assert "~" in str(e)
    assert "old" in str(e)
    assert "new" in str(e)
