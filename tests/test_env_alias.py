import pytest
from envault.env_alias import (
    load_aliases, add_alias, remove_alias, resolve_alias, apply_aliases
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_load_aliases_empty(vault_dir):
    assert load_aliases(vault_dir) == {}


def test_add_alias(vault_dir):
    add_alias(vault_dir, "DB", "DATABASE_URL")
    aliases = load_aliases(vault_dir)
    assert aliases["DB"] == "DATABASE_URL"


def test_add_alias_empty_name_raises(vault_dir):
    with pytest.raises(ValueError):
        add_alias(vault_dir, "", "DATABASE_URL")


def test_add_alias_empty_target_raises(vault_dir):
    with pytest.raises(ValueError):
        add_alias(vault_dir, "DB", "")


def test_remove_alias(vault_dir):
    add_alias(vault_dir, "DB", "DATABASE_URL")
    remove_alias(vault_dir, "DB")
    assert load_aliases(vault_dir) == {}


def test_remove_alias_missing_raises(vault_dir):
    with pytest.raises(KeyError):
        remove_alias(vault_dir, "NONEXISTENT")


def test_resolve_alias_mapped(vault_dir):
    add_alias(vault_dir, "DB", "DATABASE_URL")
    assert resolve_alias(vault_dir, "DB") == "DATABASE_URL"


def test_resolve_alias_unmapped_returns_self(vault_dir):
    assert resolve_alias(vault_dir, "UNKNOWN") == "UNKNOWN"


def test_apply_aliases_adds_aliased_keys(vault_dir):
    add_alias(vault_dir, "DB", "DATABASE_URL")
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET": "abc"}
    result = apply_aliases(vault_dir, env)
    assert result["DB"] == "postgres://localhost/db"
    assert result["DATABASE_URL"] == "postgres://localhost/db"
    assert result["SECRET"] == "abc"


def test_apply_aliases_skips_missing_target(vault_dir):
    add_alias(vault_dir, "DB", "DATABASE_URL")
    env = {"SECRET": "abc"}
    result = apply_aliases(vault_dir, env)
    assert "DB" not in result


def test_apply_aliases_preserves_original(vault_dir):
    add_alias(vault_dir, "S", "SECRET")
    env = {"SECRET": "xyz"}
    result = apply_aliases(vault_dir, env)
    assert result["SECRET"] == "xyz"
    assert result["S"] == "xyz"
