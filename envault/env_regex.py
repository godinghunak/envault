"""Regex-based key/value filtering and validation for env files."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RegexMatch:
    key: str
    value: str
    pattern: str

    def __str__(self) -> str:
        return f"{self.key}={self.value!r}  (matched: {self.pattern})"


@dataclass
class RegexResult:
    matches: List[RegexMatch] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def __len__(self) -> int:
        return len(self.matches)


def match_keys(env: Dict[str, str], pattern: str) -> RegexResult:
    """Return all entries whose key matches the given regex pattern."""
    result = RegexResult()
    try:
        rx = re.compile(pattern)
    except re.error as exc:
        result.errors.append(f"Invalid pattern {pattern!r}: {exc}")
        return result
    for k, v in env.items():
        if rx.search(k):
            result.matches.append(RegexMatch(key=k, value=v, pattern=pattern))
    return result


def match_values(env: Dict[str, str], pattern: str) -> RegexResult:
    """Return all entries whose value matches the given regex pattern."""
    result = RegexResult()
    try:
        rx = re.compile(pattern)
    except re.error as exc:
        result.errors.append(f"Invalid pattern {pattern!r}: {exc}")
        return result
    for k, v in env.items():
        if rx.search(v):
            result.matches.append(RegexMatch(key=k, value=v, pattern=pattern))
    return result


def validate_values(env: Dict[str, str], rules: Dict[str, str]) -> RegexResult:
    """Validate env values against a dict of {key: regex_pattern} rules.
    Entries that fail their rule are added to result.errors."""
    result = RegexResult()
    for key, pattern in rules.items():
        if key not in env:
            continue
        try:
            rx = re.compile(pattern)
        except re.error as exc:
            result.errors.append(f"Invalid rule pattern for {key!r}: {exc}")
            continue
        val = env[key]
        if rx.fullmatch(val):
            result.matches.append(RegexMatch(key=key, value=val, pattern=pattern))
        else:
            result.errors.append(
                f"{key}={val!r} does not match required pattern {pattern!r}"
            )
    return result


def format_regex_result(result: RegexResult) -> str:
    lines: List[str] = []
    if result.matches:
        lines.append(f"Matches ({len(result.matches)}):")
        for m in result.matches:
            lines.append(f"  {m}")
    if result.errors:
        lines.append(f"Errors ({len(result.errors)}):")
        for e in result.errors:
            lines.append(f"  {e}")
    if not lines:
        lines.append("No matches found.")
    return "\n".join(lines)
