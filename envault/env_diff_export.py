"""env_diff_export.py — Export diffs between versions to various formats (JSON, CSV, Markdown)."""

from __future__ import annotations

import csv
import io
import json
from typing import List, Dict, Optional

from envault.diff import diff_envs, parse_env
from envault.export import export_version, export_latest
from envault.vault import load_manifest


def _get_env_dict(vault_dir: str, password: str, version: Optional[int]) -> Dict[str, str]:
    """Decrypt and parse a version (or latest) into a key/value dict."""
    if version is None:
        text = export_latest(vault_dir, password)
    else:
        text = export_version(vault_dir, password, version)
    return parse_env(text)


def diff_to_json(vault_dir: str, password: str, version_a: int, version_b: int) -> str:
    """Return a JSON string describing the diff between two versions.

    Each entry has: key, change (added/removed/modified), old_value, new_value.
    """
    env_a = _get_env_dict(vault_dir, password, version_a)
    env_b = _get_env_dict(vault_dir, password, version_b)
    changes = _build_change_list(env_a, env_b)
    return json.dumps(
        {
            "version_a": version_a,
            "version_b": version_b,
            "changes": changes,
        },
        indent=2,
    )


def diff_to_csv(vault_dir: str, password: str, version_a: int, version_b: int) -> str:
    """Return a CSV string describing the diff between two versions.

    Columns: key, change, old_value, new_value.
    """
    env_a = _get_env_dict(vault_dir, password, version_a)
    env_b = _get_env_dict(vault_dir, password, version_b)
    changes = _build_change_list(env_a, env_b)

    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=["key", "change", "old_value", "new_value"]
    )
    writer.writeheader()
    for row in changes:
        writer.writerow(row)
    return buf.getvalue()


def diff_to_markdown(vault_dir: str, password: str, version_a: int, version_b: int) -> str:
    """Return a Markdown table describing the diff between two versions."""
    env_a = _get_env_dict(vault_dir, password, version_a)
    env_b = _get_env_dict(vault_dir, password, version_b)
    changes = _build_change_list(env_a, env_b)

    lines: List[str] = [
        f"## Diff: v{version_a} → v{version_b}",
        "",
        "| Key | Change | Old Value | New Value |",
        "|-----|--------|-----------|-----------|" ,
    ]
    for c in changes:
        key = c["key"]
        change = c["change"]
        old = c["old_value"] or ""
        new = c["new_value"] or ""
        lines.append(f"| `{key}` | {change} | {old} | {new} |")

    if not changes:
        lines.append("| _(no changes)_ | | | |")

    return "\n".join(lines) + "\n"


def _build_change_list(
    env_a: Dict[str, str], env_b: Dict[str, str]
) -> List[Dict[str, Optional[str]]]:
    """Compare two env dicts and return a list of change records."""
    changes: List[Dict[str, Optional[str]]] = []

    all_keys = sorted(set(env_a) | set(env_b))
    for key in all_keys:
        in_a = key in env_a
        in_b = key in env_b
        if in_a and not in_b:
            changes.append(
                {"key": key, "change": "removed", "old_value": env_a[key], "new_value": None}
            )
        elif not in_a and in_b:
            changes.append(
                {"key": key, "change": "added", "old_value": None, "new_value": env_b[key]}
            )
        elif env_a[key] != env_b[key]:
            changes.append(
                {
                    "key": key,
                    "change": "modified",
                    "old_value": env_a[key],
                    "new_value": env_b[key],
                }
            )

    return changes
