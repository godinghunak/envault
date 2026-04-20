"""Utilities to detect and fix non-uppercase env variable keys."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class UppercaseIssue:
    key: str
    line_number: int

    def __str__(self) -> str:
        return f"Line {self.line_number}: key '{self.key}' is not uppercase"


def find_non_uppercase(env_text: str) -> List[UppercaseIssue]:
    """Return a list of issues for keys that are not fully uppercase."""
    issues: List[UppercaseIssue] = []
    for lineno, line in enumerate(env_text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, _ = stripped.partition("=")
        key = key.strip()
        if key and key != key.upper():
            issues.append(UppercaseIssue(key=key, line_number=lineno))
    return issues


def uppercase_env(env_text: str) -> str:
    """Return a new env text with all keys converted to uppercase."""
    lines = []
    for line in env_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            lines.append(line)
            continue
        key, sep, rest = stripped.partition("=")
        lines.append(f"{key.strip().upper()}{sep}{rest}")
    result = "\n".join(lines)
    if env_text.endswith("\n"):
        result += "\n"
    return result


def uppercase_dict(env_dict: Dict[str, str]) -> Dict[str, str]:
    """Return a new dict with all keys converted to uppercase."""
    return {k.upper(): v for k, v in env_dict.items()}
