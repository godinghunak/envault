import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_rename import rename_key, apply_rename, list_keys
from envault.diff import parse_env
import argparse

PASSWORD = 'testpass'


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / '.env'
    p.write_text('DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=production\n')
    return str(p)


def push(vault_dir, env_file):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=PASSWORD)
    cmd_push(args)


def test_rename_key_changes_key(vault_dir, env_file):
    push(vault_dir, env_file)
    result = rename_key(vault_dir, 'DB_HOST', 'DATABASE_HOST')
    env = parse_env(result)
    assert 'DATABASE_HOST' in env
    assert 'DB_HOST' not in env
    assert env['DATABASE_HOST'] == 'localhost'


def test_rename_key_preserves_other_keys(vault_dir, env_file):
    push(vault_dir, env_file)
    result = rename_key(vault_dir, 'DB_HOST', 'DATABASE_HOST')
    env = parse_env(result)
    assert env['DB_PORT'] == '5432'
    assert env['APP_ENV'] == 'production'


def test_rename_nonexistent_key_no_change(vault_dir, env_file):
    push(vault_dir, env_file)
    result = rename_key(vault_dir, 'MISSING_KEY', 'NEW_KEY')
    env = parse_env(result)
    assert 'NEW_KEY' not in env
    assert len(env) == 3


def test_apply_rename_creates_new_version(vault_dir, env_file):
    push(vault_dir, env_file)
    new_ver = apply_rename(vault_dir, PASSWORD, 'DB_HOST', 'DATABASE_HOST')
    assert new_ver == 2


def test_list_keys_returns_sorted(vault_dir, env_file):
    push(vault_dir, env_file)
    keys = list_keys(vault_dir)
    assert keys == sorted(keys)
    assert 'DB_HOST' in keys
    assert 'DB_PORT' in keys


def test_list_keys_specific_version(vault_dir, env_file):
    push(vault_dir, env_file)
    apply_rename(vault_dir, PASSWORD, 'DB_HOST', 'DATABASE_HOST')
    keys_v1 = list_keys(vault_dir, version=1)
    keys_v2 = list_keys(vault_dir, version=2)
    assert 'DB_HOST' in keys_v1
    assert 'DATABASE_HOST' in keys_v2
    assert 'DB_HOST' not in keys_v2
