"""Profile support: named sets of env files (e.g. dev, staging, prod)."""
import json
from pathlib import Path
from envault.vault import _vault_path


def _profiles_path(vault_dir: str) -> Path:
    return _vault_path(vault_dir) / "profiles.json"


def load_profiles(vault_dir: str) -> dict:
    p = _profiles_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_profiles(vault_dir: str, profiles: dict) -> None:
    _profiles_path(vault_dir).write_text(json.dumps(profiles, indent=2))


def add_profile(vault_dir: str, name: str, env_file: str) -> None:
    profiles = load_profiles(vault_dir)
    profiles[name] = {"env_file": env_file}
    save_profiles(vault_dir, profiles)


def remove_profile(vault_dir: str, name: str) -> None:
    profiles = load_profiles(vault_dir)
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found.")
    del profiles[name]
    save_profiles(vault_dir, profiles)


def get_profile(vault_dir: str, name: str) -> dict:
    profiles = load_profiles(vault_dir)
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found.")
    return profiles[name]


def list_profiles(vault_dir: str) -> list:
    return list(load_profiles(vault_dir).keys())
