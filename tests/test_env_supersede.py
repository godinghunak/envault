"""Tests for envault.env_supersede."""
from __future__ import annotations

import pytest

from envault.env_supersede import (
    get_superseded_by,
    list_superseded,
    load_supersede,
    mark_superseded,
    unmark_superseded,
)
from envault.vault import init_vault


@pytest.fixture()
def vault_dir(tmp_path):
    d = str(tmp_path / "vault")
    init_vault(d)
    return d


def test_load_supersede_empty(vault_dir):
    assert load_supersede(vault_dir) == {}


def test_mark_superseded_stores_record(vault_dir):
    mark_superseded(vault_dir, 1, 2)
    data = load_supersede(vault_dir)
    assert data["1"] == "2"


def test_mark_superseded_self_raises(vault_dir):
    with pytest.raises(ValueError, match="cannot supersede itself"):
        mark_superseded(vault_dir, 3, 3)


def test_get_superseded_by_returns_version(vault_dir):
    mark_superseded(vault_dir, 5, 6)
    assert get_superseded_by(vault_dir, 5) == 6


def test_get_superseded_by_missing_returns_none(vault_dir):
    assert get_superseded_by(vault_dir, 99) is None


def test_unmark_superseded_removes_record(vault_dir):
    mark_superseded(vault_dir, 1, 2)
    unmark_superseded(vault_dir, 1)
    assert get_superseded_by(vault_dir, 1) is None


def test_unmark_superseded_idempotent(vault_dir):
    # Should not raise even if record doesn't exist
    unmark_superseded(vault_dir, 42)


def test_list_superseded_empty(vault_dir):
    assert list_superseded(vault_dir) == []


def test_list_superseded_multiple(vault_dir):
    mark_superseded(vault_dir, 1, 2)
    mark_superseded(vault_dir, 3, 4)
    entries = list_superseded(vault_dir)
    assert len(entries) == 2
    assert entries[0] == {"version": 1, "superseded_by": 2}
    assert entries[1] == {"version": 3, "superseded_by": 4}


def test_mark_superseded_overwrites(vault_dir):
    mark_superseded(vault_dir, 1, 2)
    mark_superseded(vault_dir, 1, 5)
    assert get_superseded_by(vault_dir, 1) == 5
