"""env_coverage.py – compute key coverage across vault versions.

For each key seen across all versions, report which versions contain it
and derive a coverage percentage.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from envault.diff import parse_env
from envault.export import export_version
from envault.vault import load_manifest


@dataclass
class KeyCoverage:
    key: str
    present_in: List[int] = field(default_factory=list)
    absent_from: List[int] = field(default_factory=list)

    @property
    def coverage_pct(self) -> float:
        total = len(self.present_in) + len(self.absent_from)
        if total == 0:
            return 0.0
        return 100.0 * len(self.present_in) / total

    def __str__(self) -> str:  # pragma: no cover
        return (
            f"{self.key}: {self.coverage_pct:.0f}% "
            f"(present in {self.present_in}, absent from {self.absent_from})"
        )


@dataclass
class CoverageReport:
    versions: List[int]
    entries: Dict[str, KeyCoverage] = field(default_factory=dict)

    @property
    def full_coverage_keys(self) -> List[str]:
        return [k for k, v in self.entries.items() if not v.absent_from]

    @property
    def partial_coverage_keys(self) -> List[str]:
        return [k for k, v in self.entries.items() if v.absent_from and v.present_in]


def compute_coverage(vault_dir: str, password: str) -> CoverageReport:
    """Decrypt every version and compute per-key coverage statistics."""
    manifest = load_manifest(vault_dir)
    versions: List[int] = manifest.get("versions", [])

    all_keys: Set[str] = set()
    version_keys: Dict[int, Set[str]] = {}

    for ver in versions:
        try:
            plaintext = export_version(vault_dir, ver, password)
            keys = set(parse_env(plaintext).keys())
        except Exception:
            keys = set()
        version_keys[ver] = keys
        all_keys |= keys

    report = CoverageReport(versions=versions)
    for key in sorted(all_keys):
        entry = KeyCoverage(key=key)
        for ver in versions:
            if key in version_keys.get(ver, set()):
                entry.present_in.append(ver)
            else:
                entry.absent_from.append(ver)
        report.entries[key] = entry

    return report


def format_coverage(report: CoverageReport) -> str:
    if not report.entries:
        return "No keys found across any version."
    lines = [f"Coverage across {len(report.versions)} version(s):"]
    for key, entry in report.entries.items():
        lines.append(
            f"  {key:<30} {entry.coverage_pct:5.0f}%  "
            f"present={entry.present_in}  absent={entry.absent_from}"
        )
    return "\n".join(lines)
