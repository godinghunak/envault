"""env_diff_summary.py — Produce a human-readable summary of changes between two vault versions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.diff import parse_env, diff_envs
from envault.export import export_version, export_latest
from envault.vault import load_manifest


@dataclass
class DiffSummary:
    version_a: str
    version_b: str
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)
    unchanged: int = 0

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.changed)

    @property
    def has_changes(self) -> bool:
        return self.total_changes > 0


def summarize_diff(vault_dir: str, version_a: str, version_b: str, password: str) -> DiffSummary:
    """Decrypt two versions and return a DiffSummary describing key-level changes."""
    text_a = export_version(vault_dir, version_a, password)
    text_b = export_version(vault_dir, version_b, password)

    env_a = parse_env(text_a)
    env_b = parse_env(text_b)

    added: List[str] = []
    removed: List[str] = []
    changed: List[str] = []
    unchanged = 0

    all_keys = set(env_a) | set(env_b)
    for key in sorted(all_keys):
        if key not in env_a:
            added.append(key)
        elif key not in env_b:
            removed.append(key)
        elif env_a[key] != env_b[key]:
            changed.append(key)
        else:
            unchanged += 1

    return DiffSummary(
        version_a=version_a,
        version_b=version_b,
        added=added,
        removed=removed,
        changed=changed,
        unchanged=unchanged,
    )


def format_diff_summary(summary: DiffSummary) -> str:
    """Return a printable string for a DiffSummary."""
    lines = [
        f"Diff summary: v{summary.version_a} → v{summary.version_b}",
        f"  Added   : {len(summary.added)}",
        f"  Removed : {len(summary.removed)}",
        f"  Changed : {len(summary.changed)}",
        f"  Unchanged: {summary.unchanged}",
    ]
    if summary.added:
        lines.append("  + " + ", ".join(summary.added))
    if summary.removed:
        lines.append("  - " + ", ".join(summary.removed))
    if summary.changed:
        lines.append("  ~ " + ", ".join(summary.changed))
    return "\n".join(lines)
