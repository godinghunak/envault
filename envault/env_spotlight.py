"""Spotlight: highlight and focus on specific keys across vault versions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import load_manifest
from envault.export import export_version
from envault.diff import parse_env


@dataclass
class SpotlightEntry:
    version: int
    key: str
    value: Optional[str]
    changed: bool = False

    def __str__(self) -> str:
        marker = "*" if self.changed else " "
        val = self.value if self.value is not None else "<missing>"
        return f"[{marker}] v{self.version:>3}  {self.key}={val}"


@dataclass
class SpotlightResult:
    key: str
    entries: List[SpotlightEntry] = field(default_factory=list)

    @property
    def versions_present(self) -> List[int]:
        return [e.version for e in self.entries if e.value is not None]

    @property
    def versions_missing(self) -> List[int]:
        return [e.version for e in self.entries if e.value is None]

    @property
    def unique_values(self) -> List[str]:
        seen = []
        for e in self.entries:
            if e.value is not None and e.value not in seen:
                seen.append(e.value)
        return seen


def spotlight_key(vault_dir: str, key: str, password: str) -> SpotlightResult:
    """Track a single key across all versions in the vault."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    result = SpotlightResult(key=key)
    prev_value: Optional[str] = None

    for version in versions:
        plaintext = export_version(vault_dir, version, password)
        env = parse_env(plaintext)
        value = env.get(key)
        changed = value != prev_value and len(result.entries) > 0
        result.entries.append(SpotlightEntry(version=version, key=key, value=value, changed=changed))
        prev_value = value

    return result


def spotlight_keys(vault_dir: str, keys: List[str], password: str) -> Dict[str, SpotlightResult]:
    """Track multiple keys across all vault versions."""
    return {key: spotlight_key(vault_dir, key, password) for key in keys}


def format_spotlight(result: SpotlightResult) -> str:
    lines = [f"Spotlight: {result.key}"]
    lines.append("-" * 40)
    if not result.entries:
        lines.append("  No versions found.")
        return "\n".join(lines)
    for entry in result.entries:
        lines.append(f"  {entry}")
    lines.append("")
    lines.append(f"  Unique values : {len(result.unique_values)}")
    lines.append(f"  Present in    : {len(result.versions_present)} version(s)")
    lines.append(f"  Missing in    : {len(result.versions_missing)} version(s)")
    return "\n".join(lines)
