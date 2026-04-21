"""Normalize .env file values: quote values with spaces, strip inline comments, etc."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class NormalizeIssue:
    line_number: int
    key: str
    original: str
    normalized: str
    reason: str

    def __str__(self) -> str:
        return f"Line {self.line_number}: {self.key} — {self.reason}"


def _strip_inline_comment(value: str) -> str:
    """Remove trailing inline comment (unquoted # preceded by whitespace)."""
    if value.startswith(("'", '"')):
        return value
    idx = value.find(' #')
    if idx != -1:
        return value[:idx].rstrip()
    return value


def _quote_if_needed(value: str) -> str:
    """Wrap value in double quotes if it contains spaces and is not already quoted."""
    if value.startswith(("'", '"')):
        return value
    if ' ' in value or '\t' in value:
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


def normalize_value(value: str) -> str:
    """Apply all normalization steps to a single value string."""
    value = _strip_inline_comment(value)
    value = _quote_if_needed(value)
    return value


def normalize_env(
    text: str,
) -> tuple[str, List[NormalizeIssue]]:
    """Normalize all key=value pairs in an .env text block.

    Returns (normalized_text, list_of_issues).
    """
    lines = text.splitlines()
    out_lines: List[str] = []
    issues: List[NormalizeIssue] = []

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            out_lines.append(line)
            continue

        if "=" not in stripped:
            out_lines.append(line)
            continue

        key, _, raw_value = stripped.partition("=")
        key = key.strip()
        norm_value = normalize_value(raw_value)

        if norm_value != raw_value:
            reasons = []
            if _strip_inline_comment(raw_value) != raw_value:
                reasons.append("inline comment stripped")
            if norm_value != _strip_inline_comment(raw_value):
                reasons.append("value quoted due to whitespace")
            reason = "; ".join(reasons) if reasons else "normalized"
            issues.append(
                NormalizeIssue(
                    line_number=lineno,
                    key=key,
                    original=raw_value,
                    normalized=norm_value,
                    reason=reason,
                )
            )
            out_lines.append(f"{key}={norm_value}")
        else:
            out_lines.append(line)

    return "\n".join(out_lines), issues
