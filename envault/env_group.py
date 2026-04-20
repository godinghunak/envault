"""Group environment variables by prefix or custom grouping rules."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple


def group_by_prefix(env: Dict[str, str], separator: str = "_") -> Dict[str, Dict[str, str]]:
    """Group env vars by their first prefix segment (e.g. DB_HOST -> group 'DB')."""
    groups: Dict[str, Dict[str, str]] = defaultdict(dict)
    for key, value in env.items():
        if separator in key:
            prefix = key.split(separator, 1)[0]
        else:
            prefix = "_OTHER"
        groups[prefix][key] = value
    return dict(groups)


def group_by_custom(env: Dict[str, str], rules: List[Tuple[str, List[str]]]) -> Dict[str, Dict[str, str]]:
    """Group env vars by custom rules: list of (group_name, [key_prefixes]).

    Keys not matching any rule land in '_OTHER'.
    """
    groups: Dict[str, Dict[str, str]] = defaultdict(dict)
    assigned: set = set()

    for group_name, prefixes in rules:
        for key, value in env.items():
            if any(key.startswith(p) for p in prefixes):
                groups[group_name][key] = value
                assigned.add(key)

    for key, value in env.items():
        if key not in assigned:
            groups["_OTHER"][key] = value

    return dict(groups)


def list_groups(grouped: Dict[str, Dict[str, str]]) -> List[str]:
    """Return sorted list of group names."""
    return sorted(grouped.keys())


def get_group(grouped: Dict[str, Dict[str, str]], name: str) -> Optional[Dict[str, str]]:
    """Return the env dict for a specific group, or None if not found."""
    return grouped.get(name)


def format_groups(grouped: Dict[str, Dict[str, str]]) -> str:
    """Format grouped env vars for display."""
    lines: List[str] = []
    for group in sorted(grouped.keys()):
        lines.append(f"[{group}]")
        for key, value in sorted(grouped[group].items()):
            lines.append(f"  {key}={value}")
    return "\n".join(lines)
