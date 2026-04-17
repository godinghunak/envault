"""Diff utilities for comparing .env file versions."""
from __future__ import annotations
from typing import Dict, List, Tuple


def parse_env(content: str) -> Dict[str, str]:
    """Parse .env content into a key-value dict, ignoring comments and blanks."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


def diff_envs(
    old: Dict[str, str], new: Dict[str, str]
) -> List[Tuple[str, str, str | None, str | None]]:
    """
    Compare two env dicts.
    Returns list of (status, key, old_value, new_value).
    status is one of: 'added', 'removed', 'changed', 'unchanged'.
    """
    results = []
    all_keys = set(old) | set(new)
    for key in sorted(all_keys):
        if key in old and key not in new:
            results.append(("removed", key, old[key], None))
        elif key not in old and key in new:
            results.append(("added", key, None, new[key]))
        elif old[key] != new[key]:
            results.append(("changed", key, old[key], new[key]))
        else:
            results.append(("unchanged", key, old[key], new[key]))
    return results


def format_diff(diff: List[Tuple[str, str, str | None, str | None]], show_values: bool = False) -> str:
    """Format diff list into a human-readable string."""
    lines = []
    for status, key, old_val, new_val in diff:
        if status == "added":
            val = f"={new_val}" if show_values else ""
            lines.append(f"+ {key}{val}")
        elif status == "removed":
            val = f"={old_val}" if show_values else ""
            lines.append(f"- {key}{val}")
        elif status == "changed":
            if show_values:
                lines.append(f"~ {key}: {old_val} -> {new_val}")
            else:
                lines.append(f"~ {key}")
        # unchanged lines are omitted
    if not lines:
        return "(no changes)"
    return "\n".join(lines)
