"""Tests for envault.env_watch."""
import time
from pathlib import Path

import pytest

from envault.env_watch import _file_hash, watch_file, make_auto_push_handler
from envault.vault import init_vault, list_versions


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return f


def test_file_hash_returns_string(env_file):
    h = _file_hash(env_file)
    assert isinstance(h, str) and len(h) == 64


def test_file_hash_changes_on_edit(env_file):
    h1 = _file_hash(env_file)
    env_file.write_text("KEY=other\n")
    h2 = _file_hash(env_file)
    assert h1 != h2


def test_watch_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        watch_file(tmp_path / "missing.env", lambda p: None, max_iterations=1)


def test_watch_detects_change(env_file):
    changes = []

    def write_after_delay():
        time.sleep(0.05)
        env_file.write_text("KEY=changed\n")

    import threading
    t = threading.Thread(target=write_after_delay)
    t.start()

    watch_file(env_file, lambda p: changes.append(str(p)), interval=0.02, max_iterations=10)
    t.join()

    assert len(changes) >= 1


def test_make_auto_push_handler_pushes_version(vault_dir, env_file):
    handler = make_auto_push_handler(vault_dir, "secret")
    assert list_versions(vault_dir) == []
    handler(env_file)
    versions = list_versions(vault_dir)
    assert len(versions) == 1


def test_make_auto_push_handler_increments_versions(vault_dir, env_file):
    handler = make_auto_push_handler(vault_dir, "secret")
    handler(env_file)
    env_file.write_text("KEY=v2\n")
    handler(env_file)
    assert len(list_versions(vault_dir)) == 2
