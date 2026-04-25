"""Scan vault versions for sensitive values that appear to be real secrets."""

import re
from dataclasses import dataclass
from typing import List, Dict

# Patterns that suggest a value is a real secret (not a placeholder)
_REAL_SECRET_PATTERNS = [
    re.compile(r'^[A-Za-z0-9+/]{32,}={0,2}$'),          # base64-like
    re.compile(r'^[0-9a-fA-F]{32,}$'),                   # hex string
    re.compile(r'^sk[-_][a-zA-Z0-9]{20,}'),              # API key prefix
    re.compile(r'^ghp_[A-Za-z0-9]{36}'),                 # GitHub token
    re.compile(r'^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'),  # JWT
    re.compile(r'^-----BEGIN'),                           # PEM key
]

_SENSITIVE_KEY_PATTERNS = [
    re.compile(r'(?i)(password|passwd|secret|token|api.?key|private.?key|auth|credential)'),
]


@dataclass
class SensitiveFinding:
    key: str
    version: int
    reason: str

    def __str__(self) -> str:
        return f"v{self.version}: {self.key} — {self.reason}"


def _is_sensitive_key(key: str) -> bool:
    return any(p.search(key) for p in _SENSITIVE_KEY_PATTERNS)


def _looks_like_real_secret(value: str) -> bool:
    if not value or len(value) < 8:
        return False
    return any(p.search(value) for p in _REAL_SECRET_PATTERNS)


def scan_dict(env: Dict[str, str], version: int) -> List[SensitiveFinding]:
    """Scan a single env dict for sensitive-looking entries."""
    findings: List[SensitiveFinding] = []
    for key, value in env.items():
        if _is_sensitive_key(key) and _looks_like_real_secret(value):
            findings.append(SensitiveFinding(
                key=key,
                version=version,
                reason="sensitive key name with high-entropy value",
            ))
    return findings


def scan_versions(versions: Dict[int, Dict[str, str]]) -> List[SensitiveFinding]:
    """Scan multiple versions and return all findings."""
    findings: List[SensitiveFinding] = []
    for version, env in versions.items():
        findings.extend(scan_dict(env, version))
    return findings


def format_findings(findings: List[SensitiveFinding]) -> str:
    if not findings:
        return "No sensitive values detected."
    lines = [f"Found {len(findings)} sensitive finding(s):"]
    for f in findings:
        lines.append(f"  {f}")
    return "\n".join(lines)
