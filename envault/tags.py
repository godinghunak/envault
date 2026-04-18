"""Tag specific vault versions with human-readable labels."""

import json
from pathlib import Path
from envault.vault import _vault_path


def _tags_path(vault_dir: str) -> Path:
    return _vault_path(vault_dir) / "tags.json"


def load_tags(vault_dir: str) -> dict:
    path = _tags_path(vault_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_tags(vault_dir: str, tags: dict) -> None:
    path = _tags_path(vault_dir)
    with open(path, "w") as f:
        json.dump(tags, f, indent=2)


def add_tag(vault_dir: str, tag: str, version: int) -> None:
    tags = load_tags(vault_dir)
    tags[tag] = version
    save_tags(vault_dir, tags)


def remove_tag(vault_dir: str, tag: str) -> None:
    tags = load_tags(vault_dir)
    if tag not in tags:
        raise KeyError(f"Tag '{tag}' not found.")
    del tags[tag]
    save_tags(vault_dir, tags)


def resolve_tag(vault_dir: str, tag: str) -> int:
    tags = load_tags(vault_dir)
    if tag not in tags:
        raise KeyError(f"Tag '{tag}' not found.")
    return tags[tag]


def list_tags(vault_dir: str) -> list:
    tags = load_tags(vault_dir)
    return [(tag, version) for tag, version in sorted(tags.items())]
