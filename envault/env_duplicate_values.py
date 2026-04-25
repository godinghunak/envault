"""Detect and report keys that share identical values within an env version."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envault.diff import parse_env


@dataclass
class DuplicateValueGroup:
    value: str
    keys: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        keys_str = ", ".join(sorted(self.keys))
        preview = self.value[:40] + "..." if len(self.value) > 40 else self.value
        return f"value={preview!r} shared by: {keys_str}"


def find_duplicate_values(env_text: str) -> List[DuplicateValueGroup]:
    """Return groups of keys that share the same value.

    Empty values are excluded from duplicate detection.
    """
    pairs = parse_env(env_text)
    value_map: Dict[str, List[str]] = {}
    for key, value in pairs.items():
        if not value:
            continue
        value_map.setdefault(value, []).append(key)

    groups = [
        DuplicateValueGroup(value=val, keys=keys)
        for val, keys in value_map.items()
        if len(keys) > 1
    ]
    groups.sort(key=lambda g: sorted(g.keys)[0])
    return groups


def format_duplicate_values(groups: List[DuplicateValueGroup]) -> str:
    """Render duplicate-value groups as a human-readable string."""
    if not groups:
        return "No duplicate values found."
    lines = ["Duplicate values detected:"]
    for g in groups:
        lines.append(f"  {g}")
    return "\n".join(lines)
