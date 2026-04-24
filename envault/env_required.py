"""Check for required keys in .env files against a required-keys list."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set


@dataclass
class MissingKeyIssue:
    key: str
    source: str = "required"

    def __str__(self) -> str:
        return f"Required key '{self.key}' is missing"


@dataclass
class RequiredCheckResult:
    missing: List[MissingKeyIssue] = field(default_factory=list)
    present: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.missing) == 0


def load_required_keys(text: str) -> Set[str]:
    """Parse a required-keys file (one key per line, # comments ignored)."""
    keys: Set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        keys.add(line.split()[0])
    return keys


def check_required(env: dict, required: Set[str]) -> RequiredCheckResult:
    """Return a RequiredCheckResult comparing env keys against required set."""
    result = RequiredCheckResult()
    for key in sorted(required):
        if key in env:
            result.present.append(key)
        else:
            result.missing.append(MissingKeyIssue(key=key))
    return result


def check_required_from_text(env_text: str, required_text: str) -> RequiredCheckResult:
    """Convenience wrapper: parse both texts and run the check."""
    from envault.diff import parse_env

    env = parse_env(env_text)
    required = load_required_keys(required_text)
    return check_required(env, required)


def format_result(result: RequiredCheckResult) -> str:
    lines: List[str] = []
    if result.ok:
        lines.append(f"All {len(result.present)} required key(s) present.")
    else:
        for issue in result.missing:
            lines.append(f"  MISSING  {issue.key}")
        for key in result.present:
            lines.append(f"  OK       {key}")
        lines.append(f"\n{len(result.missing)} missing, {len(result.present)} present.")
    return "\n".join(lines)
