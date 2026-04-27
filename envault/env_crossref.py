"""Cross-reference checker: find keys used in one version but missing in another."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from envault.diff import parse_env
from envault.vault import load_manifest
from envault.export import export_version, export_latest
from envault.crypto import decrypt_file


@dataclass
class CrossRefIssue:
    key: str
    present_in: int
    missing_in: int

    def __str__(self) -> str:
        return f"Key '{self.key}' exists in v{self.present_in} but is missing in v{self.missing_in}"


@dataclass
class CrossRefResult:
    issues: List[CrossRefIssue] = field(default_factory=list)
    version_a: int = 0
    version_b: int = 0

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def only_in_a(self) -> List[CrossRefIssue]:
        return [i for i in self.issues if i.missing_in == self.version_b]

    def only_in_b(self) -> List[CrossRefIssue]:
        return [i for i in self.issues if i.missing_in == self.version_a]


def crossref_versions(
    vault_dir: str,
    password: str,
    version_a: int,
    version_b: int,
) -> CrossRefResult:
    """Compare keys present in version_a vs version_b and report discrepancies."""
    text_a = export_version(vault_dir, password, version_a)
    text_b = export_version(vault_dir, password, version_b)

    keys_a: Set[str] = set(parse_env(text_a).keys())
    keys_b: Set[str] = set(parse_env(text_b).keys())

    result = CrossRefResult(version_a=version_a, version_b=version_b)

    for key in keys_a - keys_b:
        result.issues.append(CrossRefIssue(key=key, present_in=version_a, missing_in=version_b))

    for key in keys_b - keys_a:
        result.issues.append(CrossRefIssue(key=key, present_in=version_b, missing_in=version_a))

    result.issues.sort(key=lambda i: (i.missing_in, i.key))
    return result


def format_crossref(result: CrossRefResult) -> str:
    """Return a human-readable summary of cross-reference issues."""
    if result.ok:
        return f"No cross-reference issues between v{result.version_a} and v{result.version_b}."

    lines = [f"Cross-reference issues between v{result.version_a} and v{result.version_b}:"]
    for issue in result.issues:
        lines.append(f"  - {issue}")
    return "\n".join(lines)
