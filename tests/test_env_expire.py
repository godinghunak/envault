import time
import pytest
from envault.vault import init_vault
from envault.env_expire import (
    set_expiry, get_expiry, is_expired, list_expired, clear_expiry, load_expiry
)
from envault.commands import cmd_push
import argparse


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


def push(vault_dir, env_file, password="pw"):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=str(env_file), password=password)
    cmd_push(args)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\nFOO=bar\n")
    return f


def test_load_expiry_empty(vault_dir):
    assert load_expiry(vault_dir) == {}


def test_set_expiry_stores_timestamp(vault_dir, env_file):
    push(vault_dir, env_file)
    exp = set_expiry(vault_dir, 1, ttl_seconds=3600)
    assert exp > time.time()
    assert get_expiry(vault_dir, 1) == pytest.approx(exp, abs=1)


def test_set_expiry_invalid_version_raises(vault_dir):
    with pytest.raises(ValueError, match="does not exist"):
        set_expiry(vault_dir, 99, ttl_seconds=60)


def test_set_expiry_invalid_ttl_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(ValueError, match="positive"):
        set_expiry(vault_dir, 1, ttl_seconds=0)


def test_get_expiry_none_when_not_set(vault_dir, env_file):
    push(vault_dir, env_file)
    assert get_expiry(vault_dir, 1) is None


def test_is_expired_false_for_future(vault_dir, env_file):
    push(vault_dir, env_file)
    set_expiry(vault_dir, 1, ttl_seconds=3600)
    assert not is_expired(vault_dir, 1)


def test_is_expired_true_for_past(vault_dir, env_file):
    push(vault_dir, env_file)
    set_expiry(vault_dir, 1, ttl_seconds=1)
    # Manually backdate
    from envault.env_expire import load_expiry, save_expiry
    data = load_expiry(vault_dir)
    data["1"] = time.time() - 10
    save_expiry(vault_dir, data)
    assert is_expired(vault_dir, 1)


def test_list_expired_returns_expired_versions(vault_dir, env_file):
    push(vault_dir, env_file)
    from envault.env_expire import load_expiry, save_expiry
    data = load_expiry(vault_dir)
    data["1"] = time.time() - 5
    save_expiry(vault_dir, data)
    assert 1 in list_expired(vault_dir)


def test_clear_expiry_removes_entry(vault_dir, env_file):
    push(vault_dir, env_file)
    set_expiry(vault_dir, 1, ttl_seconds=60)
    assert clear_expiry(vault_dir, 1) is True
    assert get_expiry(vault_dir, 1) is None


def test_clear_expiry_missing_returns_false(vault_dir, env_file):
    push(vault_dir, env_file)
    assert clear_expiry(vault_dir, 1) is False
