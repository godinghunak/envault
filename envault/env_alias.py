"""Key aliasing: map one key name to another across versions."""

import json
from pathlib import Path


def _aliases_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "aliases.json"


def load_aliases(vault_dir: str) -> dict:
    p = _aliases_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_aliases(vault_dir: str, aliases: dict) -> None:
    _aliases_path(vault_dir).write_text(json.dumps(aliases, indent=2))


def add_alias(vault_dir: str, alias: str, target: str) -> None:
    """Map alias -> target key name."""
    if not alias or not target:
        raise ValueError("Alias and target must be non-empty strings.")
    aliases = load_aliases(vault_dir)
    aliases[alias] = target
    save_aliases(vault_dir, aliases)


def remove_alias(vault_dir: str, alias: str) -> None:
    aliases = load_aliases(vault_dir)
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' not found.")
    del aliases[alias]
    save_aliases(vault_dir, aliases)


def resolve_alias(vault_dir: str, alias: str) -> str:
    """Return the target key for an alias, or the alias itself if not mapped."""
    aliases = load_aliases(vault_dir)
    return aliases.get(alias, alias)


def apply_aliases(vault_dir: str, env_dict: dict) -> dict:
    """Return a new dict with aliased keys added (original keys preserved)."""
    aliases = load_aliases(vault_dir)
    result = dict(env_dict)
    for alias, target in aliases.items():
        if target in env_dict:
            result[alias] = env_dict[target]
    return result
