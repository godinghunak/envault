import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.search import search_key, search_value, search_in_version


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n")
    return str(f)


def push(vault_dir, env_file, password="pass"):
    import argparse
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def test_search_key_finds_match(vault_dir, env_file):
    push(vault_dir, env_file)
    results = search_key(vault_dir, "pass", "DB_*")
    keys = [r["key"] for r in results]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_search_key_no_match(vault_dir, env_file):
    push(vault_dir, env_file)
    results = search_key(vault_dir, "pass", "NONEXISTENT_*")
    assert results == []


def test_search_value_finds_match(vault_dir, env_file):
    push(vault_dir, env_file)
    results = search_value(vault_dir, "pass", "localhost")
    assert any(r["key"] == "DB_HOST" for r in results)


def test_search_across_versions(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    f2 = tmp_path / ".env2"
    f2.write_text("DB_HOST=remotehost\nNEW_VAR=hello\n")
    push(vault_dir, str(f2))
    results = search_key(vault_dir, "pass", "DB_HOST")
    assert len(results) == 2
    versions = [r["version"] for r in results]
    assert 1 in versions
    assert 2 in versions


def test_search_in_version(vault_dir, env_file):
    push(vault_dir, env_file)
    results = search_in_version(vault_dir, "pass", 1, "DB_*")
    assert "DB_HOST" in results
    assert results["DB_HOST"] == "localhost"


def test_search_in_version_invalid(vault_dir):
    with pytest.raises(ValueError, match="Version 99 not found"):
        search_in_version(vault_dir, "pass", 99, "*")
