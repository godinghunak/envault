"""Tests for envault/tags.py"""

import pytest
from envault.vault import init_vault
from envault.tags import add_tag, remove_tag, list_tags, resolve_tag, load_tags


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d)
    return d


def test_load_tags_empty(vault_dir):
    assert load_tags(vault_dir) == {}


def test_add_tag(vault_dir):
    add_tag(vault_dir, "release-1.0", 1)
    tags = load_tags(vault_dir)
    assert tags["release-1.0"] == 1


def test_list_tags(vault_dir):
    add_tag(vault_dir, "beta", 2)
    add_tag(vault_dir, "alpha", 1)
    result = list_tags(vault_dir)
    assert result == [("alpha", 1), ("beta", 2)]


def test_resolve_tag(vault_dir):
    add_tag(vault_dir, "stable", 3)
    assert resolve_tag(vault_dir, "stable") == 3


def test_resolve_missing_tag_raises(vault_dir):
    with pytest.raises(KeyError, match="not found"):
        resolve_tag(vault_dir, "nonexistent")


def test_remove_tag(vault_dir):
    add_tag(vault_dir, "v1", 1)
    remove_tag(vault_dir, "v1")
    assert "v1" not in load_tags(vault_dir)


def test_remove_missing_tag_raises(vault_dir):
    with pytest.raises(KeyError, match="not found"):
        remove_tag(vault_dir, "ghost")


def test_overwrite_tag(vault_dir):
    add_tag(vault_dir, "latest", 1)
    add_tag(vault_dir, "latest", 5)
    assert resolve_tag(vault_dir, "latest") == 5
