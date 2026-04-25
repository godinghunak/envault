"""Read-only key protection: mark keys as read-only to prevent accidental modification."""

import json
from pathlib import Path
from typing import Dict, List, Optional


def _readonly_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault" / "readonly.json"


def load_readonly(vault_dir: str) -> Dict[str, str]:
    """Return dict of {key: reason} for all read-only keys."""
    path = _readonly_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_readonly(vault_dir: str, data: Dict[str, str]) -> None:
    path = _readonly_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def protect_key(vault_dir: str, key: str, reason: str = "") -> None:
    """Mark a key as read-only with an optional reason."""
    if not key.strip():
        raise ValueError("Key must not be empty.")
    data = load_readonly(vault_dir)
    data[key] = reason
    save_readonly(vault_dir, data)


def unprotect_key(vault_dir: str, key: str) -> None:
    """Remove read-only protection from a key."""
    data = load_readonly(vault_dir)
    if key not in data:
        raise KeyError(f"Key '{key}' is not protected.")
    del data[key]
    save_readonly(vault_dir, data)


def list_protected(vault_dir: str) -> List[str]:
    """Return sorted list of protected key names."""
    return sorted(load_readonly(vault_dir).keys())


def is_protected(vault_dir: str, key: str) -> bool:
    """Return True if the key is marked read-only."""
    return key in load_readonly(vault_dir)


def check_protected(vault_dir: str, env_dict: Dict[str, str], base_dict: Optional[Dict[str, str]] = None) -> List[str]:
    """Return list of violations: protected keys whose values differ from base_dict.
    If base_dict is None, any presence of a protected key is reported."""
    data = load_readonly(vault_dir)
    violations = []
    for key in data:
        if base_dict is None:
            if key in env_dict:
                violations.append(key)
        else:
            if key in env_dict and key in base_dict and env_dict[key] != base_dict[key]:
                violations.append(key)
    return violations
