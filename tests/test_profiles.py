import pytest
from envault.vault import init_vault
from envault.profiles import (
    add_profile, remove_profile, list_profiles, get_profile, load_profiles
)


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d)
    return d


def test_load_profiles_empty(vault_dir):
    assert load_profiles(vault_dir) == {}


def test_add_profile(vault_dir):
    add_profile(vault_dir, "dev", ".env.dev")
    profiles = load_profiles(vault_dir)
    assert "dev" in profiles
    assert profiles["dev"]["env_file"] == ".env.dev"


def test_list_profiles(vault_dir):
    add_profile(vault_dir, "dev", ".env.dev")
    add_profile(vault_dir, "prod", ".env.prod")
    names = list_profiles(vault_dir)
    assert "dev" in names
    assert "prod" in names


def test_get_profile(vault_dir):
    add_profile(vault_dir, "staging", ".env.staging")
    info = get_profile(vault_dir, "staging")
    assert info["env_file"] == ".env.staging"


def test_get_profile_missing(vault_dir):
    with pytest.raises(KeyError, match="not found"):
        get_profile(vault_dir, "nonexistent")


def test_remove_profile(vault_dir):
    add_profile(vault_dir, "dev", ".env.dev")
    remove_profile(vault_dir, "dev")
    assert "dev" not in list_profiles(vault_dir)


def test_remove_profile_missing(vault_dir):
    with pytest.raises(KeyError, match="not found"):
        remove_profile(vault_dir, "ghost")


def test_add_multiple_profiles_persisted(vault_dir):
    add_profile(vault_dir, "a", ".env.a")
    add_profile(vault_dir, "b", ".env.b")
    profiles = load_profiles(vault_dir)
    assert len(profiles) == 2
