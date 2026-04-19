"""Detect and validate placeholder values in .env files."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
import re

PLACEHOLDER_PATTERNS = [
    re.compile(r'^<.+>$'),
    re.compile(r'^\{\{.+\}\}$'),
    re.compile(r'^CHANGE_ME$', re.IGNORECASE),
    re.compile(r'^TODO$', re.IGNORECASE),
    re.compile(r'^YOUR_.+$', re.IGNORECASE),
    re.compile(r'^PLACEHOLDER$', re.IGNORECASE),
    re.compile(r'^FIXME$', re.IGNORECASE),
    re.compile(r'^\$\{.+\}$'),
]


@dataclass
class PlaceholderIssue:
    key: str
    value: str
    pattern: str

    def __str__(self) -> str:
        return f"{self.key}={self.value!r} matches placeholder pattern '{self.pattern}'"


def is_placeholder(value: str) -> str | None:
    """Return the matched pattern string if value looks like a placeholder, else None."""
    for pat in PLACEHOLDER_PATTERNS:
        if pat.match(value):
            return pat.pattern
    return None


def find_placeholders(env: Dict[str, str]) -> List[PlaceholderIssue]:
    """Return a list of PlaceholderIssue for any placeholder values found."""
    issues = []
    for key, value in env.items():
        matched = is_placeholder(value)
        if matched:
            issues.append(PlaceholderIssue(key=key, value=value, pattern=matched))
    return issues


def find_placeholders_in_text(text: str) -> List[PlaceholderIssue]:
    """Parse raw env text and return placeholder issues."""
    env: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, _, value = line.partition('=')
            env[key.strip()] = value.strip()
    return find_placeholders(env)
