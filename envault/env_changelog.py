"""Generate a human-readable changelog between vault versions."""

from dataclasses import dataclass, field
from typing import List, Optional
from envault.diff import parse_env, diff_envs


@dataclass
class ChangelogEntry:
    version: int
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    modified: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    def __str__(self) -> str:
        lines = [f"Version {self.version}:"]
        for k in self.added:
            lines.append(f"  + {k}")
        for k in self.removed:
            lines.append(f"  - {k}")
        for k in self.modified:
            lines.append(f"  ~ {k}")
        if not self.has_changes():
            lines.append("  (no changes)")
        return "\n".join(lines)


def build_changelog(
    vault_dir: str,
    password: str,
    from_version: Optional[int] = None,
    to_version: Optional[int] = None,
) -> List[ChangelogEntry]:
    """Build a changelog list between two versions (inclusive)."""
    from envault.vault import load_manifest
    from envault.export import export_version

    manifest = load_manifest(vault_dir)
    versions = sorted(manifest.get("versions", []))
    if not versions:
        return []

    start = from_version if from_version is not None else (versions[0] if len(versions) > 1 else versions[0])
    end = to_version if to_version is not None else versions[-1]

    selected = [v for v in versions if start <= v <= end]
    if len(selected) < 2:
        return []

    entries = []
    for i in range(1, len(selected)):
        prev_v = selected[i - 1]
        curr_v = selected[i]
        prev_text = export_version(vault_dir, password, prev_v)
        curr_text = export_version(vault_dir, password, curr_v)
        prev_env = parse_env(prev_text)
        curr_env = parse_env(curr_text)
        diffs = diff_envs(prev_env, curr_env)
        entry = ChangelogEntry(version=curr_v)
        for d in diffs:
            if d.status == "added":
                entry.added.append(d.key)
            elif d.status == "removed":
                entry.removed.append(d.key)
            elif d.status == "modified":
                entry.modified.append(d.key)
        entries.append(entry)
    return entries


def format_changelog(entries: List[ChangelogEntry]) -> str:
    """Render changelog entries as a string."""
    if not entries:
        return "No changelog entries."
    return "\n\n".join(str(e) for e in entries)
