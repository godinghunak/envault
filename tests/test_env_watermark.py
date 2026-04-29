"""Tests for envault.env_watermark."""

import pytest

from envault.vault import init_vault
from envault.env_watermark import (
    load_watermarks,
    stamp,
    verify,
    get_watermark,
    list_watermarks,
    remove_watermark,
)


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / ".vault")
    init_vault(d)
    return d


def test_load_watermarks_empty(vault_dir):
    assert load_watermarks(vault_dir) == {}


def test_stamp_returns_hex_string(vault_dir):
    mark = stamp(vault_dir, version=1, author="alice", secret="s3cr3t")
    assert isinstance(mark, str)
    assert len(mark) == 64  # sha256 hex


def test_stamp_stores_entry(vault_dir):
    stamp(vault_dir, version=1, author="alice", secret="s3cr3t", note="release")
    wm = load_watermarks(vault_dir)
    assert "1" in wm
    assert wm["1"]["author"] == "alice"
    assert wm["1"]["note"] == "release"
    assert "mark" in wm["1"]
    assert "ts" in wm["1"]


def test_verify_valid(vault_dir):
    stamp(vault_dir, version=2, author="bob", secret="topsecret")
    assert verify(vault_dir, version=2, author="bob", secret="topsecret") is True


def test_verify_wrong_secret(vault_dir):
    stamp(vault_dir, version=3, author="carol", secret="correct")
    assert verify(vault_dir, version=3, author="carol", secret="wrong") is False


def test_verify_wrong_author(vault_dir):
    stamp(vault_dir, version=4, author="dave", secret="abc")
    assert verify(vault_dir, version=4, author="eve", secret="abc") is False


def test_verify_missing_version(vault_dir):
    assert verify(vault_dir, version=99, author="x", secret="y") is False


def test_get_watermark_returns_entry(vault_dir):
    stamp(vault_dir, version=1, author="alice", secret="s")
    entry = get_watermark(vault_dir, 1)
    assert entry is not None
    assert entry["author"] == "alice"


def test_get_watermark_missing_returns_none(vault_dir):
    assert get_watermark(vault_dir, 42) is None


def test_list_watermarks_empty(vault_dir):
    assert list_watermarks(vault_dir) == []


def test_list_watermarks_sorted(vault_dir):
    stamp(vault_dir, version=3, author="c", secret="s")
    stamp(vault_dir, version=1, author="a", secret="s")
    stamp(vault_dir, version=2, author="b", secret="s")
    entries = list_watermarks(vault_dir)
    assert [e["version"] for e in entries] == [1, 2, 3]


def test_remove_watermark_existing(vault_dir):
    stamp(vault_dir, version=1, author="a", secret="s")
    result = remove_watermark(vault_dir, 1)
    assert result is True
    assert get_watermark(vault_dir, 1) is None


def test_remove_watermark_missing(vault_dir):
    result = remove_watermark(vault_dir, 99)
    assert result is False


def test_stamp_is_deterministic(vault_dir):
    m1 = stamp(vault_dir, version=1, author="x", secret="y")
    m2 = stamp(vault_dir, version=1, author="x", secret="y")
    assert m1 == m2


def test_different_secrets_produce_different_marks(vault_dir):
    m1 = stamp(vault_dir, version=1, author="x", secret="aaa")
    m2 = stamp(vault_dir, version=1, author="x", secret="bbb")
    assert m1 != m2
