import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.env_annotate import (
    load_annotations, set_annotation, remove_annotation,
    get_annotation, list_annotations
)


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / "vault")
    init_vault(d)
    return d


def test_load_annotations_empty(vault_dir):
    assert load_annotations(vault_dir, 1) == {}


def test_set_annotation_stores_note(vault_dir):
    set_annotation(vault_dir, 1, "DB_HOST", "Primary database host")
    assert get_annotation(vault_dir, 1, "DB_HOST") == "Primary database host"


def test_set_annotation_overwrites(vault_dir):
    set_annotation(vault_dir, 1, "API_KEY", "old note")
    set_annotation(vault_dir, 1, "API_KEY", "new note")
    assert get_annotation(vault_dir, 1, "API_KEY") == "new note"


def test_get_annotation_missing_key_returns_none(vault_dir):
    assert get_annotation(vault_dir, 1, "MISSING") is None


def test_remove_annotation(vault_dir):
    set_annotation(vault_dir, 1, "FOO", "bar")
    remove_annotation(vault_dir, 1, "FOO")
    assert get_annotation(vault_dir, 1, "FOO") is None


def test_remove_missing_annotation_raises(vault_dir):
    with pytest.raises(KeyError):
        remove_annotation(vault_dir, 1, "NONEXISTENT")


def test_list_annotations_returns_all(vault_dir):
    set_annotation(vault_dir, 2, "A", "note a")
    set_annotation(vault_dir, 2, "B", "note b")
    items = list_annotations(vault_dir, 2)
    assert ("A", "note a") in items
    assert ("B", "note b") in items
    assert len(items) == 2


def test_annotations_are_version_isolated(vault_dir):
    set_annotation(vault_dir, 1, "KEY", "v1 note")
    set_annotation(vault_dir, 2, "KEY", "v2 note")
    assert get_annotation(vault_dir, 1, "KEY") == "v1 note"
    assert get_annotation(vault_dir, 2, "KEY") == "v2 note"


def test_annotations_persisted_to_disk(vault_dir):
    set_annotation(vault_dir, 3, "PERSIST", "saved")
    reloaded = load_annotations(vault_dir, 3)
    assert reloaded["PERSIST"] == "saved"
