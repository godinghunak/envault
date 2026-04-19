"""Redact sensitive values in .env content for safe display."""

import re
from typing import Optional

SENSITIVE_PATTERNS = [
    re.compile(r'(password|passwd|pwd|secret|token|key|api_key|auth|credential)', re.IGNORECASE),
]

REDACT_PLACEHOLDER = "***REDACTED***"


def is_sensitive(key: str) -> bool:
    """Return True if the key name looks sensitive."""
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(key):
            return True
    return False


def redact_line(line: str) -> str:
    """Redact the value of a sensitive key in a single .env line."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return line
    if "=" not in stripped:
        return line
    key, _, value = stripped.partition("=")
    key = key.strip()
    if is_sensitive(key) and value.strip():
        return f"{key}={REDACT_PLACEHOLDER}\n"
    return line


def redact_env(content: str) -> str:
    """Return a copy of .env content with sensitive values redacted."""
    lines = content.splitlines(keepends=True)
    return "".join(redact_line(line) for line in lines)


def redact_dict(env: dict) -> dict:
    """Return a copy of an env dict with sensitive values replaced."""
    return {
        k: (REDACT_PLACEHOLDER if is_sensitive(k) and v else v)
        for k, v in env.items()
    }
