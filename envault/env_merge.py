"""Merge two env versions or files, with conflict detection."""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from envault.diff import parse_env
from envault.export import export_version, export_latest
from envault.vault import load_manifest


@dataclass
class MergeConflict:
    key: str
    base_value: Optional[str]
    theirs_value: Optional[str]

    def __str__(self):
        return f"CONFLICT {self.key!r}: base={self.base_value!r} theirs={self.theirs_value!r}"


@dataclass
class MergeResult:
    merged: Dict[str, str]
    conflicts: List[MergeConflict] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0


def merge_dicts(
    base: Dict[str, str],
    ours: Dict[str, str],
    theirs: Dict[str, str],
) -> MergeResult:
    """Three-way merge. Ours wins unless theirs changed from base and ours did not."""
    all_keys = set(base) | set(ours) | set(theirs)
    merged: Dict[str, str] = {}
    conflicts: List[MergeConflict] = []

    for key in sorted(all_keys):
        b = base.get(key)
        o = ours.get(key)
        t = theirs.get(key)

        if o == t:
            if o is not None:
                merged[key] = o
        elif b == o:
            # ours unchanged, take theirs
            if t is not None:
                merged[key] = t
        elif b == t:
            # theirs unchanged, take ours
            if o is not None:
                merged[key] = o
        else:
            # both changed differently
            conflicts.append(MergeConflict(key, b, t))
            merged[key] = o if o is not None else t  # keep ours as default

    return MergeResult(merged=merged, conflicts=conflicts)


def merge_versions(
    vault_dir: str,
    base_version: int,
    our_version: int,
    their_version: int,
    password: str,
) -> MergeResult:
    base = parse_env(export_version(vault_dir, base_version, password))
    ours = parse_env(export_version(vault_dir, our_version, password))
    theirs = parse_env(export_version(vault_dir, their_version, password))
    return merge_dicts(base, ours, theirs)


def format_merged(merged: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in sorted(merged.items())) + "\n"
