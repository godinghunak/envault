"""Truncate long values in .env files to a maximum length."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


DEFAULT_MAX_LENGTH = 100
TRUNCATION_SUFFIX = "..."


@dataclass
class TruncationChange:
    key: str
    original_length: int
    truncated_length: int

    def __str__(self) -> str:
        return (
            f"{self.key}: {self.original_length} chars "
            f"-> {self.truncated_length} chars (truncated)"
        )


def truncate_value(value: str, max_length: int = DEFAULT_MAX_LENGTH) -> str:
    """Truncate a single value to max_length, appending suffix if truncated."""
    if len(value) <= max_length:
        return value
    keep = max_length - len(TRUNCATION_SUFFIX)
    if keep < 0:
        keep = 0
    return value[:keep] + TRUNCATION_SUFFIX


def truncate_dict(
    env: Dict[str, str],
    max_length: int = DEFAULT_MAX_LENGTH,
    keys: Optional[List[str]] = None,
) -> tuple[Dict[str, str], List[TruncationChange]]:
    """Return a new dict with values truncated and a list of changes made."""
    result: Dict[str, str] = {}
    changes: List[TruncationChange] = []
    for k, v in env.items():
        if keys is not None and k not in keys:
            result[k] = v
            continue
        truncated = truncate_value(v, max_length)
        result[k] = truncated
        if truncated != v:
            changes.append(TruncationChange(k, len(v), len(truncated)))
    return result, changes


def truncate_env_text(
    text: str,
    max_length: int = DEFAULT_MAX_LENGTH,
    keys: Optional[List[str]] = None,
) -> tuple[str, List[TruncationChange]]:
    """Truncate values in raw .env text, preserving comments and blank lines."""
    lines_out: List[str] = []
    changes: List[TruncationChange] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            lines_out.append(line)
            continue
        if "=" not in line:
            lines_out.append(line)
            continue
        key, _, value = line.partition("=")
        key_stripped = key.strip()
        if keys is not None and key_stripped not in keys:
            lines_out.append(line)
            continue
        truncated = truncate_value(value, max_length)
        lines_out.append(f"{key}={truncated}")
        if truncated != value:
            changes.append(TruncationChange(key_stripped, len(value), len(truncated)))
    return "\n".join(lines_out), changes
