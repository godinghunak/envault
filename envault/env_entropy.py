"""Entropy analysis for .env values — detect weak or low-entropy secrets."""

import math
from collections import Counter
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class EntropyResult:
    key: str
    value: str
    entropy: float
    is_weak: bool
    reason: str

    def __str__(self) -> str:
        status = "WEAK" if self.is_weak else "OK"
        return f"[{status}] {self.key}: entropy={self.entropy:.2f}  ({self.reason})"


MIN_SECRET_LENGTH = 8
WEAK_ENTROPY_THRESHOLD = 3.0  # bits per character
SENSITIVE_SUBSTRINGS = ("password", "secret", "token", "key", "api", "auth", "pass")


def _shannon_entropy(value: str) -> float:
    """Compute Shannon entropy (bits per character) for a string."""
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def _is_sensitive_key(key: str) -> bool:
    lower = key.lower()
    return any(sub in lower for sub in SENSITIVE_SUBSTRINGS)


def analyze_value(key: str, value: str) -> EntropyResult:
    """Analyse a single key/value pair for entropy weakness."""
    entropy = _shannon_entropy(value)
    is_weak = False
    reason = "sufficient entropy"

    if not value:
        is_weak = _is_sensitive_key(key)
        reason = "empty value"
    elif _is_sensitive_key(key):
        if len(value) < MIN_SECRET_LENGTH:
            is_weak = True
            reason = f"value too short ({len(value)} < {MIN_SECRET_LENGTH})"
        elif entropy < WEAK_ENTROPY_THRESHOLD:
            is_weak = True
            reason = f"low entropy ({entropy:.2f} < {WEAK_ENTROPY_THRESHOLD})"

    return EntropyResult(key=key, value=value, entropy=entropy, is_weak=is_weak, reason=reason)


def analyze_dict(env: Dict[str, str]) -> List[EntropyResult]:
    """Analyse all key/value pairs in an env dict."""
    return [analyze_value(k, v) for k, v in env.items()]


def weak_results(results: List[EntropyResult]) -> List[EntropyResult]:
    """Filter to only weak results."""
    return [r for r in results if r.is_weak]


def format_entropy_report(results: List[EntropyResult], only_weak: bool = False) -> str:
    """Format a list of EntropyResult objects into a human-readable report."""
    items = weak_results(results) if only_weak else results
    if not items:
        return "No issues found." if only_weak else "No keys to analyse."
    return "\n".join(str(r) for r in items)
