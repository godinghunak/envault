"""Track version lineage: parent-child relationships between vault versions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _lineage_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault" / "lineage.json"


def load_lineage(vault_dir: str) -> Dict[int, Optional[int]]:
    """Return mapping of version -> parent_version (or None for root)."""
    p = _lineage_path(vault_dir)
    if not p.exists():
        return {}
    return {int(k): v for k, v in json.loads(p.read_text()).items()}


def save_lineage(vault_dir: str, lineage: Dict[int, Optional[int]]) -> None:
    p = _lineage_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({str(k): v for k, v in lineage.items()}, indent=2))


def record_version(vault_dir: str, version: int, parent: Optional[int] = None) -> None:
    """Record that *version* was derived from *parent* (None = initial commit)."""
    lineage = load_lineage(vault_dir)
    lineage[version] = parent
    save_lineage(vault_dir, lineage)


def ancestors(vault_dir: str, version: int) -> List[int]:
    """Return ordered list of ancestor versions, oldest first."""
    lineage = load_lineage(vault_dir)
    chain: List[int] = []
    current: Optional[int] = lineage.get(version)
    while current is not None:
        chain.append(current)
        current = lineage.get(current)
    chain.reverse()
    return chain


def descendants(vault_dir: str, version: int) -> List[int]:
    """Return all versions that descend from *version* (direct and indirect)."""
    lineage = load_lineage(vault_dir)
    result: List[int] = []
    frontier = {version}
    while frontier:
        children = {v for v, p in lineage.items() if p in frontier}
        children -= {version}  # exclude self
        new = children - set(result) - frontier
        result.extend(sorted(new))
        frontier = new
    return sorted(result)


def lineage_chain(vault_dir: str, version: int) -> List[int]:
    """Full chain from root ancestor to *version*, inclusive."""
    return ancestors(vault_dir, version) + [version]
