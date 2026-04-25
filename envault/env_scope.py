"""Scope management: restrict visible keys per named scope."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _scopes_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "scopes.json"


def load_scopes(vault_dir: str) -> Dict[str, List[str]]:
    """Return {scope_name: [key, ...]} mapping."""
    p = _scopes_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_scopes(vault_dir: str, scopes: Dict[str, List[str]]) -> None:
    p = _scopes_path(vault_dir)
    p.write_text(json.dumps(scopes, indent=2))


def add_scope(vault_dir: str, name: str, keys: List[str]) -> None:
    """Create or replace a scope with the given key list."""
    if not name:
        raise ValueError("Scope name must not be empty.")
    if not keys:
        raise ValueError("Scope must contain at least one key.")
    scopes = load_scopes(vault_dir)
    scopes[name] = sorted(set(keys))
    save_scopes(vault_dir, scopes)


def remove_scope(vault_dir: str, name: str) -> None:
    """Delete a scope by name."""
    scopes = load_scopes(vault_dir)
    if name not in scopes:
        raise KeyError(f"Scope '{name}' does not exist.")
    del scopes[name]
    save_scopes(vault_dir, scopes)


def get_scope(vault_dir: str, name: str) -> Optional[List[str]]:
    """Return the key list for a scope, or None if not found."""
    return load_scopes(vault_dir).get(name)


def list_scopes(vault_dir: str) -> List[str]:
    """Return sorted list of scope names."""
    return sorted(load_scopes(vault_dir).keys())


def apply_scope(env: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Return a filtered dict containing only the keys in the scope."""
    return {k: v for k, v in env.items() if k in keys}
