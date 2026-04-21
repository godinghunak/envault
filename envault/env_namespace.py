"""Namespace support: group env keys under logical namespaces with prefix mapping."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import _vault_path


def _namespaces_path(vault_dir: str) -> Path:
    return _vault_path(vault_dir) / "namespaces.json"


def load_namespaces(vault_dir: str) -> Dict[str, str]:
    """Return mapping of namespace -> prefix string."""
    p = _namespaces_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_namespaces(vault_dir: str, namespaces: Dict[str, str]) -> None:
    p = _namespaces_path(vault_dir)
    p.write_text(json.dumps(namespaces, indent=2))


def add_namespace(vault_dir: str, name: str, prefix: str) -> None:
    """Register a namespace with a key prefix (e.g. 'db' -> 'DB_')."""
    if not name:
        raise ValueError("Namespace name must not be empty.")
    if not prefix:
        raise ValueError("Namespace prefix must not be empty.")
    ns = load_namespaces(vault_dir)
    ns[name] = prefix.upper()
    save_namespaces(vault_dir, ns)


def remove_namespace(vault_dir: str, name: str) -> None:
    ns = load_namespaces(vault_dir)
    if name not in ns:
        raise KeyError(f"Namespace '{name}' not found.")
    del ns[name]
    save_namespaces(vault_dir, ns)


def list_namespaces(vault_dir: str) -> List[str]:
    return sorted(load_namespaces(vault_dir).keys())


def keys_in_namespace(env: Dict[str, str], prefix: str) -> Dict[str, str]:
    """Return keys whose name starts with the given prefix."""
    upper = prefix.upper()
    return {k: v for k, v in env.items() if k.upper().startswith(upper)}


def resolve_namespace(vault_dir: str, name: str) -> Optional[str]:
    ns = load_namespaces(vault_dir)
    return ns.get(name)
