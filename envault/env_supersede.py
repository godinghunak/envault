"""env_supersede.py – mark a vault version as superseded by another."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _supersede_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".supersede.json"


def load_supersede(vault_dir: str) -> Dict[str, str]:
    """Return mapping of version -> superseded_by version."""
    p = _supersede_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_supersede(vault_dir: str, data: Dict[str, str]) -> None:
    _supersede_path(vault_dir).write_text(json.dumps(data, indent=2))


def mark_superseded(vault_dir: str, version: int, superseded_by: int) -> None:
    """Mark *version* as superseded by *superseded_by*."""
    if version == superseded_by:
        raise ValueError("A version cannot supersede itself.")
    data = load_supersede(vault_dir)
    data[str(version)] = str(superseded_by)
    save_supersede(vault_dir, data)


def unmark_superseded(vault_dir: str, version: int) -> None:
    """Remove supersede record for *version* (idempotent)."""
    data = load_supersede(vault_dir)
    data.pop(str(version), None)
    save_supersede(vault_dir, data)


def get_superseded_by(vault_dir: str, version: int) -> Optional[int]:
    """Return the version that supersedes *version*, or None."""
    data = load_supersede(vault_dir)
    val = data.get(str(version))
    return int(val) if val is not None else None


def list_superseded(vault_dir: str) -> List[Dict[str, int]]:
    """Return all supersede relationships as a list of dicts."""
    data = load_supersede(vault_dir)
    return [
        {"version": int(k), "superseded_by": int(v)}
        for k, v in sorted(data.items(), key=lambda x: int(x[0]))
    ]
