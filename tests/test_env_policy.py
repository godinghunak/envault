import pytest
from envault.env_policy import (
    load_policy, save_policy, set_rule, remove_rule,
    enforce_policy, PolicyViolation
)
from envault.vault import init_vault


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


def test_load_policy_empty(vault_dir):
    assert load_policy(vault_dir) == {}


def test_set_rule_stores_value(vault_dir):
    set_rule(vault_dir, "no_empty_values", True)
    policy = load_policy(vault_dir)
    assert policy["no_empty_values"] is True


def test_set_rule_overwrites(vault_dir):
    set_rule(vault_dir, "max_keys", 5)
    set_rule(vault_dir, "max_keys", 10)
    assert load_policy(vault_dir)["max_keys"] == 10


def test_remove_rule(vault_dir):
    set_rule(vault_dir, "max_keys", 5)
    remove_rule(vault_dir, "max_keys")
    assert "max_keys" not in load_policy(vault_dir)


def test_remove_missing_rule_raises(vault_dir):
    with pytest.raises(KeyError):
        remove_rule(vault_dir, "nonexistent")


def test_enforce_require_keys_pass(vault_dir):
    set_rule(vault_dir, "require_keys", ["DB_HOST", "DB_PORT"])
    violations = enforce_policy(vault_dir, {"DB_HOST": "localhost", "DB_PORT": "5432"})
    assert violations == []


def test_enforce_require_keys_fail(vault_dir):
    set_rule(vault_dir, "require_keys", ["DB_HOST", "SECRET_KEY"])
    violations = enforce_policy(vault_dir, {"DB_HOST": "localhost"})
    assert any("SECRET_KEY" in v for v in violations)


def test_enforce_forbidden_keys(vault_dir):
    set_rule(vault_dir, "forbidden_keys", ["DEBUG"])
    violations = enforce_policy(vault_dir, {"DEBUG": "true", "API_KEY": "abc"})
    assert any("DEBUG" in v for v in violations)


def test_enforce_max_keys(vault_dir):
    set_rule(vault_dir, "max_keys", 2)
    violations = enforce_policy(vault_dir, {"A": "1", "B": "2", "C": "3"})
    assert any("Too many" in v for v in violations)


def test_enforce_no_empty_values(vault_dir):
    set_rule(vault_dir, "no_empty_values", True)
    violations = enforce_policy(vault_dir, {"KEY": ""})
    assert any("Empty value" in v for v in violations)


def test_enforce_no_violations_empty_policy(vault_dir):
    violations = enforce_policy(vault_dir, {"ANYTHING": "value"})
    assert violations == []
