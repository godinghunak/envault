import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.env_reorder import reorder_env, reorder_version, reorder_latest
from envault.crypto import encrypt_file
from envault.vault import add_version


ENV_TEXT = """DB_HOST=localhost
API_KEY=secret
APP_NAME=myapp
DEBUG=true
"""


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    init_vault(str(d))
    return str(d)


def push(vault_dir, content=ENV_TEXT, password="pw"):
    return add_version(vault_dir, content.encode(), password)


def test_reorder_env_explicit_order():
    result = reorder_env(ENV_TEXT, ["APP_NAME", "DEBUG", "API_KEY", "DB_HOST"])
    lines = [l for l in result.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == ["APP_NAME", "DEBUG", "API_KEY", "DB_HOST"]


def test_reorder_env_alphabetical():
    result = reorder_env(ENV_TEXT, [], alphabetical=True)
    lines = [l for l in result.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(["DB_HOST", "API_KEY", "APP_NAME", "DEBUG"])


def test_reorder_env_partial_order():
    result = reorder_env(ENV_TEXT, ["DEBUG"])
    lines = [l for l in result.splitlines() if "=" in l]
    assert lines[0].startswith("DEBUG")


def test_reorder_env_unknown_keys_ignored():
    result = reorder_env(ENV_TEXT, ["NONEXISTENT", "API_KEY"])
    lines = [l for l in result.splitlines() if "=" in l]
    assert lines[0].startswith("API_KEY")


def test_reorder_env_preserves_values():
    result = reorder_env(ENV_TEXT, [], alphabetical=True)
    assert "DB_HOST=localhost" in result
    assert "API_KEY=secret" in result


def test_reorder_version_creates_new_version(vault_dir):
    v1 = push(vault_dir)
    v2 = reorder_version(vault_dir, v1, "pw", ["DEBUG", "APP_NAME"])
    assert v2 == v1 + 1


def test_reorder_latest_no_versions_raises(vault_dir):
    with pytest.raises(ValueError, match="No versions"):
        reorder_latest(vault_dir, "pw", [], alphabetical=True)


def test_reorder_latest_returns_new_version(vault_dir):
    push(vault_dir)
    v2 = reorder_latest(vault_dir, "pw", [], alphabetical=True)
    assert v2 == 2
