"""Detect and normalize encoding issues in .env file values."""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class EncodingIssue:
    key: str
    value: str
    reason: str

    def __str__(self) -> str:
        return f"[{self.key}] {self.reason}: {self.value!r}"


_NON_ASCII_SAFE_KEYS = {"DATABASE_URL", "SECRET_KEY", "API_KEY"}


def find_encoding_issues(env: Dict[str, str]) -> List[EncodingIssue]:
    """Scan a dict of env vars for encoding-related issues."""
    issues: List[EncodingIssue] = []
    for key, value in env.items():
        # Check for non-printable ASCII control characters (except tab)
        for ch in value:
            code = ord(ch)
            if code < 0x20 and code != 0x09:
                issues.append(EncodingIssue(key, value, "contains control character"))
                break
        else:
            # Check for non-ASCII characters
            try:
                value.encode("ascii")
            except UnicodeEncodeError:
                issues.append(EncodingIssue(key, value, "contains non-ASCII characters"))
    return issues


def normalize_encoding(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new dict with values stripped of leading/trailing whitespace
    and with unicode normalized to NFC form."""
    import unicodedata
    return {
        k: unicodedata.normalize("NFC", v.strip())
        for k, v in env.items()
    }


def encoding_issues_from_text(text: str) -> List[EncodingIssue]:
    """Parse raw .env text and return encoding issues found."""
    env: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        env[key.strip()] = value.strip()
    return find_encoding_issues(env)


def format_encoding_report(issues: List[EncodingIssue]) -> str:
    """Format a list of encoding issues as a human-readable report."""
    if not issues:
        return "No encoding issues found."
    lines = [f"Found {len(issues)} encoding issue(s):"]
    for issue in issues:
        lines.append(f"  - {issue}")
    return "\n".join(lines)
