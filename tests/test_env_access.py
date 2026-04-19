import pytest
from envault.env_access import (
    grant, revoke, list_grants, can_access, filter_env, load_access
)


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    d.mkdir()
    return str(tmp_path)


def test_load_access_empty(vault_dir):
    assert load_access(vault_dir) == {}


def test_grant_adds_key(vault_dir):
    grant(vault_dir, "dev", "DB_HOST")
    assert "DB_HOST" in list_grants(vault_dir, "dev")


def test_grant_idempotent(vault_dir):
    grant(vault_dir, "dev", "DB_HOST")
    grant(vault_dir, "dev", "DB_HOST")
    assert list_grants(vault_dir, "dev").count("DB_HOST") == 1


def test_revoke_removes_key(vault_dir):
    grant(vault_dir, "dev", "DB_HOST")
    revoke(vault_dir, "dev", "DB_HOST")
    assert "DB_HOST" not in list_grants(vault_dir, "dev")


def test_revoke_removes_role_when_empty(vault_dir):
    grant(vault_dir, "dev", "DB_HOST")
    revoke(vault_dir, "dev", "DB_HOST")
    data = load_access(vault_dir)
    assert "dev" not in data


def test_revoke_nonexistent_key_is_safe(vault_dir):
    revoke(vault_dir, "dev", "MISSING")  # should not raise


def test_can_access_true(vault_dir):
    grant(vault_dir, "admin", "SECRET")
    assert can_access(vault_dir, "admin", "SECRET") is True


def test_can_access_false(vault_dir):
    assert can_access(vault_dir, "guest", "SECRET") is False


def test_filter_env_returns_allowed_keys(vault_dir):
    grant(vault_dir, "dev", "DB_HOST")
    grant(vault_dir, "dev", "DB_PORT")
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "x"}
    result = filter_env(vault_dir, "dev", env)
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_filter_env_no_grants_returns_empty(vault_dir):
    env = {"DB_HOST": "localhost"}
    assert filter_env(vault_dir, "nobody", env) == {}


def test_multiple_roles_independent(vault_dir):
    grant(vault_dir, "dev", "DB_HOST")
    grant(vault_dir, "ops", "SECRET")
    assert can_access(vault_dir, "dev", "SECRET") is False
    assert can_access(vault_dir, "ops", "DB_HOST") is False
