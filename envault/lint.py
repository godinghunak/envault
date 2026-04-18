"""Lint .env files for common issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class LintIssue:
    line: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"Line {self.line} [{self.code}]: {self.message}"


def lint_env(content: str) -> List[LintIssue]:
    """Lint env file content and return list of issues."""
    issues: List[LintIssue] = []
    seen_keys: dict[str, int] = {}

    for lineno, raw in enumerate(content.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            issues.append(LintIssue(lineno, "E001", f"Missing '=' in line: {raw!r}"))
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            issues.append(LintIssue(lineno, "E002", "Empty key"))
            continue

        if " " in key:
            issues.append(LintIssue(lineno, "E003", f"Key contains spaces: {key!r}"))

        if key != key.upper():
            issues.append(LintIssue(lineno, "W001", f"Key not uppercase: {key!r}"))

        if key in seen_keys:
            issues.append(LintIssue(lineno, "W002", f"Duplicate key {key!r} (first at line {seen_keys[key]})"))
        else:
            seen_keys[key] = lineno

        if value.startswith(("'", '"')) and not (value.endswith(value[0]) and len(value) > 1):
            issues.append(LintIssue(lineno, "W003", f"Possibly unclosed quote for key {key!r}"))

        if not value:
            issues.append(LintIssue(lineno, "W004", f"Empty value for key {key!r}"))

    return issues
