"""Drift detection: compare a live .env file against a stored vault version."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.diff import parse_env


@dataclass
class DriftEntry:
    key: str
    kind: str          # 'added' | 'removed' | 'changed'
    vault_value: Optional[str] = None
    file_value: Optional[str] = None

    def __str__(self) -> str:
        if self.kind == "added":
            return f"+ {self.key}={self.file_value}  (not in vault)"
        if self.kind == "removed":
            return f"- {self.key}={self.vault_value}  (missing from file)"
        return f"~ {self.key}: vault={self.vault_value!r}  file={self.file_value!r}"


@dataclass
class DriftResult:
    entries: List[DriftEntry] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.entries)

    def by_kind(self, kind: str) -> List[DriftEntry]:
        return [e for e in self.entries if e.kind == kind]


def detect_drift(vault_env: Dict[str, str], file_env: Dict[str, str]) -> DriftResult:
    """Return a DriftResult describing differences between vault and file."""
    result = DriftResult()
    all_keys = set(vault_env) | set(file_env)
    for key in sorted(all_keys):
        in_vault = key in vault_env
        in_file = key in file_env
        if in_vault and not in_file:
            result.entries.append(DriftEntry(key, "removed", vault_value=vault_env[key]))
        elif in_file and not in_vault:
            result.entries.append(DriftEntry(key, "added", file_value=file_env[key]))
        elif vault_env[key] != file_env[key]:
            result.entries.append(
                DriftEntry(key, "changed", vault_value=vault_env[key], file_value=file_env[key])
            )
    return result


def detect_drift_from_text(vault_text: str, file_text: str) -> DriftResult:
    return detect_drift(parse_env(vault_text), parse_env(file_text))


def format_drift(result: DriftResult) -> str:
    if not result.has_drift:
        return "No drift detected."
    lines = []
    for entry in result.entries:
        lines.append(str(entry))
    added = len(result.by_kind("added"))
    removed = len(result.by_kind("removed"))
    changed = len(result.by_kind("changed"))
    lines.append(f"\nSummary: {added} added, {removed} removed, {changed} changed.")
    return "\n".join(lines)
