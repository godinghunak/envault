"""Tests for envault.audit module."""
import pytest
from pathlib import Path
from envault.audit import log_event, read_events, clear_log, _audit_path


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_log_event_creates_file(vault_dir):
    log_event("push", {"version": 1, "file": ".env"}, vault_dir)
    assert _audit_path(vault_dir).exists()


def test_log_event_contains_action(vault_dir):
    log_event("push", {"version": 1}, vault_dir)
    events = read_events(vault_dir)
    assert len(events) == 1
    assert events[0]["action"] == "push"


def test_log_event_contains_details(vault_dir):
    log_event("pull", {"version": 2, "file": ".env"}, vault_dir)
    events = read_events(vault_dir)
    assert events[0]["version"] == 2
    assert events[0]["file"] == ".env"


def test_log_event_has_timestamp(vault_dir):
    log_event("init", {}, vault_dir)
    events = read_events(vault_dir)
    assert "timestamp" in events[0]


def test_multiple_events(vault_dir):
    log_event("push", {"version": 1}, vault_dir)
    log_event("pull", {"version": 1}, vault_dir)
    log_event("push", {"version": 2}, vault_dir)
    events = read_events(vault_dir)
    assert len(events) == 3


def test_read_events_empty(vault_dir):
    assert read_events(vault_dir) == []


def test_clear_log(vault_dir):
    log_event("push", {"version": 1}, vault_dir)
    clear_log(vault_dir)
    assert read_events(vault_dir) == []


def test_clear_log_no_file(vault_dir):
    # Should not raise
    clear_log(vault_dir)
