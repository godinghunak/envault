"""Mask sensitive values in env output, replacing with partial or full redaction."""

import re
from typing import Dict, Optional

SENSITIVE_PATTERNS = re.compile(
    r"(password|secret|token|api[_]?key|private[_]?key|auth|credential|passwd)",
    re.IGNORECASE,
)

DEFAULT_MASK = "****"


def is_sensitive(key: str) -> bool:
    return bool(SENSITIVE_PATTERNS.search(key))


def mask_value(value: str, show_chars: int = 0, mask: str = DEFAULT_MASK) -> str:
    """Mask a value, optionally revealing the last `show_chars` characters."""
    if not value:
        return mask
    if show_chars > 0 and len(value) > show_chars:
        return mask + value[-show_chars:]
    return mask


def mask_dict(
    env: Dict[str, str],
    show_chars: int = 0,
    mask: str = DEFAULT_MASK,
    keys: Optional[list] = None,
) -> Dict[str, str]:
    """Return a copy of env dict with sensitive values masked."""
    result = {}
    for k, v in env.items():
        if keys is not None:
            result[k] = mask_value(v, show_chars, mask) if k in keys else v
        elif is_sensitive(k):
            result[k] = mask_value(v, show_chars, mask)
        else:
            result[k] = v
    return result


def mask_env_text(
    text: str,
    show_chars: int = 0,
    mask: str = DEFAULT_MASK,
) -> str:
    """Mask sensitive values in raw .env text, preserving comments and blanks."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            lines.append(line)
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip()
        if is_sensitive(key):
            value = mask_value(value, show_chars, mask)
        lines.append(f"{key}={value}")
    return "\n".join(lines)
