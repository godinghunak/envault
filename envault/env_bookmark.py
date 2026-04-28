"""Bookmark specific vault versions with named labels for quick access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _bookmarks_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "bookmarks.json"


def load_bookmarks(vault_dir: str) -> Dict[str, int]:
    """Return mapping of bookmark name -> version number."""
    p = _bookmarks_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_bookmarks(vault_dir: str, bookmarks: Dict[str, int]) -> None:
    p = _bookmarks_path(vault_dir)
    p.write_text(json.dumps(bookmarks, indent=2))


def add_bookmark(vault_dir: str, name: str, version: int) -> None:
    """Create or overwrite a bookmark."""
    if not name or not name.strip():
        raise ValueError("Bookmark name must not be empty.")
    if version < 1:
        raise ValueError(f"Invalid version number: {version}")
    bookmarks = load_bookmarks(vault_dir)
    bookmarks[name] = version
    save_bookmarks(vault_dir, bookmarks)


def remove_bookmark(vault_dir: str, name: str) -> None:
    """Remove a bookmark by name; raises KeyError if not found."""
    bookmarks = load_bookmarks(vault_dir)
    if name not in bookmarks:
        raise KeyError(f"Bookmark '{name}' not found.")
    del bookmarks[name]
    save_bookmarks(vault_dir, bookmarks)


def resolve_bookmark(vault_dir: str, name: str) -> Optional[int]:
    """Return the version number for a bookmark, or None if absent."""
    return load_bookmarks(vault_dir).get(name)


def list_bookmarks(vault_dir: str) -> List[tuple]:
    """Return sorted list of (name, version) tuples."""
    return sorted(load_bookmarks(vault_dir).items())
