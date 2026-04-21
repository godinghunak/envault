"""Type-checking for .env values: detect and enforce expected types."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional


KNOWN_TYPES = ("int", "float", "bool", "url", "email", "uuid", "str")

_PATTERNS: Dict[str, re.Pattern] = {
    "int": re.compile(r"^-?\d+$"),
    "float": re.compile(r"^-?\d+\.\d+$"),
    "bool": re.compile(r"^(true|false|1|0|yes|no)$", re.IGNORECASE),
    "url": re.compile(r"^https?://[^\s]+$", re.IGNORECASE),
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
    "uuid": re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    ),
}


@dataclass
class TypeViolation:
    key: str
    value: str
    expected_type: str
    line: int

    def __str__(self) -> str:
        return (
            f"Line {self.line}: {self.key}={self.value!r} "
            f"does not match expected type '{self.expected_type}'"
        )


def detect_type(value: str) -> str:
    """Infer the most specific type for a value string."""
    for type_name in ("int", "float", "bool", "uuid", "url", "email"):
        if _PATTERNS[type_name].match(value):
            return type_name
    return "str"


def check_value(value: str, expected_type: str) -> bool:
    """Return True if value matches the expected type."""
    if expected_type == "str":
        return True
    pattern = _PATTERNS.get(expected_type)
    if pattern is None:
        raise ValueError(f"Unknown type: {expected_type!r}. Known: {KNOWN_TYPES}")
    return bool(pattern.match(value))


def typecheck_env(
    env_text: str, schema: Dict[str, str]
) -> List[TypeViolation]:
    """
    Check each key in env_text against the type declared in schema.

    schema maps key names to expected type strings, e.g. {"PORT": "int"}.
    Returns a list of TypeViolation for every mismatch.
    """
    violations: List[TypeViolation] = []
    for lineno, raw in enumerate(env_text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in schema:
            if not check_value(value, schema[key]):
                violations.append(
                    TypeViolation(
                        key=key,
                        value=value,
                        expected_type=schema[key],
                        line=lineno,
                    )
                )
    return violations
