"""Tests for envault.env_lineage."""

import pytest

from envault.env_lineage import (
    ancestors,
    descendants,
    lineage_chain,
    load_lineage,
    record_version,
)
from envault.vault import init_vault


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d)
    return d


def test_load_lineage_empty(vault_dir):
    assert load_lineage(vault_dir) == {}


def test_record_root_version(vault_dir):
    record_version(vault_dir, 1, parent=None)
    lineage = load_lineage(vault_dir)
    assert lineage[1] is None


def test_record_child_version(vault_dir):
    record_version(vault_dir, 1, parent=None)
    record_version(vault_dir, 2, parent=1)
    lineage = load_lineage(vault_dir)
    assert lineage[2] == 1


def test_ancestors_root_has_none(vault_dir):
    record_version(vault_dir, 1, parent=None)
    assert ancestors(vault_dir, 1) == []


def test_ancestors_single_parent(vault_dir):
    record_version(vault_dir, 1, parent=None)
    record_version(vault_dir, 2, parent=1)
    assert ancestors(vault_dir, 2) == [1]


def test_ancestors_chain(vault_dir):
    record_version(vault_dir, 1, parent=None)
    record_version(vault_dir, 2, parent=1)
    record_version(vault_dir, 3, parent=2)
    assert ancestors(vault_dir, 3) == [1, 2]


def test_descendants_no_children(vault_dir):
    record_version(vault_dir, 1, parent=None)
    assert descendants(vault_dir, 1) == []


def test_descendants_direct_child(vault_dir):
    record_version(vault_dir, 1, parent=None)
    record_version(vault_dir, 2, parent=1)
    assert descendants(vault_dir, 1) == [2]


def test_descendants_multi_level(vault_dir):
    record_version(vault_dir, 1, parent=None)
    record_version(vault_dir, 2, parent=1)
    record_version(vault_dir, 3, parent=2)
    result = descendants(vault_dir, 1)
    assert 2 in result
    assert 3 in result


def test_lineage_chain_root_only(vault_dir):
    record_version(vault_dir, 1, parent=None)
    assert lineage_chain(vault_dir, 1) == [1]


def test_lineage_chain_three_versions(vault_dir):
    record_version(vault_dir, 1, parent=None)
    record_version(vault_dir, 2, parent=1)
    record_version(vault_dir, 3, parent=2)
    assert lineage_chain(vault_dir, 3) == [1, 2, 3]


def test_lineage_persists_across_loads(vault_dir):
    record_version(vault_dir, 1, parent=None)
    record_version(vault_dir, 2, parent=1)
    lineage = load_lineage(vault_dir)
    assert lineage[1] is None
    assert lineage[2] == 1
