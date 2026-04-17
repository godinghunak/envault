"""Tests for envault.rollback module."""

import os
import pytest
from envault.vault import init_vault, push_version
from envault.rollback import rollback, list_versions


PASSWORD = "test-password"
ENV_CONTENT = b"DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / "vault")
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_bytes(ENV_CONTENT)
    return str(p)


def test_list_versions_empty(vault_dir):
    result = list_versions(vault_dir, ".env")
    assert result == []


def test_list_versions_after_push(vault_dir, env_file):
    push_version(vault_dir, ".env", env_file, PASSWORD)
    push_version(vault_dir, ".env", env_file, PASSWORD)
    versions = list_versions(vault_dir, ".env")
    assert len(versions) == 2
    assert versions[0]["version"] == 1
    assert versions[1]["version"] == 2


def test_rollback_restores_content(vault_dir, env_file, tmp_path):
    push_version(vault_dir, ".env", env_file, PASSWORD)
    output = str(tmp_path / "restored.env")
    rollback(vault_dir, ".env", 1, PASSWORD, output)
    assert os.path.exists(output)
    assert open(output, "rb").read() == ENV_CONTENT


def test_rollback_invalid_version_raises(vault_dir, env_file):
    push_version(vault_dir, ".env", env_file, PASSWORD)
    with pytest.raises(ValueError, match="Version 99 not found"):
        rollback(vault_dir, ".env", 99, PASSWORD, "/tmp/out.env")


def test_rollback_no_versions_raises(vault_dir, tmp_path):
    with pytest.raises(ValueError, match="No versions found"):
        rollback(vault_dir, ".env", 1, PASSWORD, str(tmp_path / "out.env"))


def test_rollback_wrong_password_raises(vault_dir, env_file, tmp_path):
    push_version(vault_dir, ".env", env_file, PASSWORD)
    output = str(tmp_path / "out.env")
    with pytest.raises(Exception):
        rollback(vault_dir, ".env", 1, "wrong-password", output)


def test_rollback_logs_event(vault_dir, env_file, tmp_path):
    from envault.audit import read_events
    push_version(vault_dir, ".env", env_file, PASSWORD)
    output = str(tmp_path / "out.env")
    rollback(vault_dir, ".env", 1, PASSWORD, output)
    events = read_events(vault_dir)
    actions = [e["action"] for e in events]
    assert "rollback" in actions
