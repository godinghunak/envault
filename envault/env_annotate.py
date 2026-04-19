"""Annotation support: attach comments/notes to env keys in a version."""
from __future__ import annotations
import json
from pathlib import Path
from envault.vault import _vault_path


def _annotations_path(vault_dir: str, version: int) -> Path:
    return Path(_vault_path(vault_dir)) / f"annotations_v{version}.json"


def load_annotations(vault_dir: str, version: int) -> dict[str, str]:
    p = _annotations_path(vault_dir, version)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_annotations(vault_dir: str, version: int, annotations: dict[str, str]) -> None:
    p = _annotations_path(vault_dir, version)
    p.write_text(json.dumps(annotations, indent=2))


def set_annotation(vault_dir: str, version: int, key: str, note: str) -> None:
    ann = load_annotations(vault_dir, version)
    ann[key] = note
    save_annotations(vault_dir, version, ann)


def remove_annotation(vault_dir: str, version: int, key: str) -> None:
    ann = load_annotations(vault_dir, version)
    if key not in ann:
        raise KeyError(f"No annotation for key '{key}' in version {version}")
    del ann[key]
    save_annotations(vault_dir, version, ann)


def get_annotation(vault_dir: str, version: int, key: str) -> str | None:
    return load_annotations(vault_dir, version).get(key)


def list_annotations(vault_dir: str, version: int) -> list[tuple[str, str]]:
    return list(load_annotations(vault_dir, version).items())
