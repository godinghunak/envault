"""Tests for envault.env_namespace module."""
import pytest
from envault.vault import init_vault
from envault.env_namespace import (
    load_namespaces,
    add_namespace,
    remove_namespace,
    list_namespaces,
    keys_in_namespace,
    resolve_namespace,
)


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d)
    return d


def test_load_namespaces_empty(vault_dir):
    assert load_namespaces(vault_dir) == {}


def test_add_namespace(vault_dir):
    add_namespace(vault_dir, "db", "DB_")
    ns = load_namespaces(vault_dir)
    assert "db" in ns
    assert ns["db"] == "DB_"


def test_add_namespace_normalizes_prefix_to_uppercase(vault_dir):
    add_namespace(vault_dir, "aws", "aws_")
    assert load_namespaces(vault_dir)["aws"] == "AWS_"


def test_add_namespace_empty_name_raises(vault_dir):
    with pytest.raises(ValueError, match="name"):
        add_namespace(vault_dir, "", "PREFIX_")


def test_add_namespace_empty_prefix_raises(vault_dir):
    with pytest.raises(ValueError, match="prefix"):
        add_namespace(vault_dir, "myns", "")


def test_remove_namespace(vault_dir):
    add_namespace(vault_dir, "cache", "CACHE_")
    remove_namespace(vault_dir, "cache")
    assert "cache" not in load_namespaces(vault_dir)


def test_remove_namespace_missing_raises(vault_dir):
    with pytest.raises(KeyError):
        remove_namespace(vault_dir, "nonexistent")


def test_list_namespaces(vault_dir):
    add_namespace(vault_dir, "db", "DB_")
    add_namespace(vault_dir, "aws", "AWS_")
    names = list_namespaces(vault_dir)
    assert names == ["aws", "db"]


def test_keys_in_namespace_matches_prefix(vault_dir):
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp"}
    result = keys_in_namespace(env, "DB_")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_keys_in_namespace_case_insensitive_prefix(vault_dir):
    env = {"DB_HOST": "localhost", "APP_NAME": "myapp"}
    result = keys_in_namespace(env, "db_")
    assert "DB_HOST" in result


def test_resolve_namespace_returns_prefix(vault_dir):
    add_namespace(vault_dir, "redis", "REDIS_")
    assert resolve_namespace(vault_dir, "redis") == "REDIS_"


def test_resolve_namespace_missing_returns_none(vault_dir):
    assert resolve_namespace(vault_dir, "ghost") is None
