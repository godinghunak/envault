"""Tests for envault.env_timestamp."""

from datetime import datetime, timezone

import pytest

from envault.env_timestamp import (
    delete_timestamp,
    format_timestamp,
    get_timestamp,
    list_timestamps,
    load_timestamps,
    record_timestamp,
)
from envault.vault import init_vault


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / "vault")
    init_vault(d)
    return d


def test_load_timestamps_empty(vault_dir):
    assert load_timestamps(vault_dir) == {}


def test_record_timestamp_returns_iso_string(vault_dir):
    iso = record_timestamp(vault_dir, 1)
    assert isinstance(iso, str)
    assert "T" in iso  # ISO 8601 separator


def test_record_timestamp_stores_value(vault_dir):
    iso = record_timestamp(vault_dir, 1)
    assert get_timestamp(vault_dir, 1) == iso


def test_get_timestamp_missing_returns_none(vault_dir):
    assert get_timestamp(vault_dir, 99) is None


def test_record_timestamp_uses_provided_datetime(vault_dir):
    dt = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    iso = record_timestamp(vault_dir, 2, dt=dt)
    assert "2024-06-15" in iso
    assert get_timestamp(vault_dir, 2) == iso


def test_record_timestamp_overwrites_existing(vault_dir):
    record_timestamp(vault_dir, 1)
    dt2 = datetime(2025, 1, 1, tzinfo=timezone.utc)
    iso2 = record_timestamp(vault_dir, 1, dt=dt2)
    assert get_timestamp(vault_dir, 1) == iso2


def test_list_timestamps_sorted(vault_dir):
    record_timestamp(vault_dir, 3)
    record_timestamp(vault_dir, 1)
    record_timestamp(vault_dir, 2)
    pairs = list_timestamps(vault_dir)
    versions = [v for v, _ in pairs]
    assert versions == [1, 2, 3]


def test_list_timestamps_empty(vault_dir):
    assert list_timestamps(vault_dir) == []


def test_format_timestamp_readable(vault_dir):
    dt = datetime(2024, 3, 22, 9, 5, 7, tzinfo=timezone.utc)
    iso = record_timestamp(vault_dir, 1, dt=dt)
    readable = format_timestamp(iso)
    assert readable == "2024-03-22 09:05:07 UTC"


def test_delete_timestamp_removes_entry(vault_dir):
    record_timestamp(vault_dir, 1)
    result = delete_timestamp(vault_dir, 1)
    assert result is True
    assert get_timestamp(vault_dir, 1) is None


def test_delete_timestamp_missing_returns_false(vault_dir):
    assert delete_timestamp(vault_dir, 42) is False
