"""Compare two .env files or vault versions for key coverage and conflicts."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envault.diff import parse_env
from envault.export import export_version, export_latest


@dataclass
class CompareResult:
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    same_value: List[str] = field(default_factory=list)
    different_value: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.only_in_a or self.only_in_b or self.different_value)


def compare_dicts(a: Dict[str, str], b: Dict[str, str]) -> CompareResult:
    keys_a = set(a)
    keys_b = set(b)
    result = CompareResult()
    result.only_in_a = sorted(keys_a - keys_b)
    result.only_in_b = sorted(keys_b - keys_a)
    for key in sorted(keys_a & keys_b):
        if a[key] == b[key]:
            result.same_value.append(key)
        else:
            result.different_value.append(key)
    return result


def compare_versions(vault_dir: str, password: str, ver_a: int, ver_b: int) -> CompareResult:
    content_a = export_version(vault_dir, password, ver_a)
    content_b = export_version(vault_dir, password, ver_b)
    return compare_dicts(parse_env(content_a), parse_env(content_b))


def compare_file_to_version(
    vault_dir: str,
    password: str,
    filepath: str,
    version: Optional[int] = None,
) -> CompareResult:
    with open(filepath) as f:
        file_content = f.read()
    if version is None:
        vault_content = export_latest(vault_dir, password)
    else:
        vault_content = export_version(vault_dir, password, version)
    return compare_dicts(parse_env(file_content), parse_env(vault_content))


def format_compare(result: CompareResult, label_a: str = "A", label_b: str = "B") -> str:
    lines = []
    for key in result.only_in_a:
        lines.append(f"  only in {label_a}: {key}")
    for key in result.only_in_b:
        lines.append(f"  only in {label_b}: {key}")
    for key in result.different_value:
        lines.append(f"  conflict:         {key}")
    for key in result.same_value:
        lines.append(f"  match:            {key}")
    return "\n".join(lines) if lines else "  (no keys found)"
