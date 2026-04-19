"""Blame: show which push introduced each key in the latest (or given) version."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

from envault.vault import load_manifest, list_versions
from envault.export import export_version
from envault.diff import parse_env


@dataclass
class BlameLine:
    key: str
    value: str
    version: int
    introduced_at: str  # ISO timestamp from manifest entry

    def __str__(self) -> str:
        return f"v{self.version} ({self.introduced_at})  {self.key}={self.value}"


def blame(vault_dir: str, password: str, version: Optional[int] = None) -> List[BlameLine]:
    """Return a BlameLine for every key, indicating when it was first introduced."""
    manifest = load_manifest(vault_dir)
    versions = list_versions(vault_dir)
    if not versions:
        return []

    target = version if version is not None else max(versions)
    if target not in versions:
        raise ValueError(f"Version {target} not found in vault.")

    # Build ordered list of versions up to target
    history = sorted(v for v in versions if v <= target)

    # Walk history oldest-first; record first appearance of each key
    first_seen: Dict[str, BlameLine] = {}
    for v in history:
        content = export_version(vault_dir, password, v)
        env = parse_env(content)
        entry = next((e for e in manifest.get("versions", []) if e["version"] == v), {})
        ts = entry.get("timestamp", "unknown")
        for key, value in env.items():
            if key not in first_seen:
                first_seen[key] = BlameLine(key=key, value=value, version=v, introduced_at=ts)

    # Return in key-sorted order
    return sorted(first_seen.values(), key=lambda b: b.key)
