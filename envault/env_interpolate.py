"""env_interpolate.py — Interpolate environment variable references within .env values.

Supports ${VAR} and $VAR syntax, with optional default values via ${VAR:-default}.
Provides cycle detection to prevent infinite loops.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# Matches ${VAR}, ${VAR:-default}, or $VAR (bare)
_INTERP_RE = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-(.*?))?\}|\$([A-Za-z_][A-Za-z0-9_]*)')


@dataclass
class InterpolationError(Exception):
    key: str
    message: str

    def __str__(self) -> str:
        return f"InterpolationError in '{self.key}': {self.message}"


@dataclass
class InterpolationResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved: List[str] = field(default_factory=list)
    cycles: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.unresolved and not self.cycles


def _resolve_value(
    key: str,
    env: Dict[str, str],
    resolved: Dict[str, str],
    visiting: set,
) -> str:
    """Recursively resolve a single key's value, detecting cycles."""
    if key in resolved:
        return resolved[key]

    if key not in env:
        raise KeyError(key)

    if key in visiting:
        raise InterpolationError(key, f"cycle detected involving '{key}'")

    visiting.add(key)
    raw = env[key]

    def _replacer(m: re.Match) -> str:
        ref_key = m.group(1) or m.group(3)
        default = m.group(2)  # may be None
        if ref_key == key:
            raise InterpolationError(key, f"self-reference detected")
        if ref_key in env:
            return _resolve_value(ref_key, env, resolved, visiting)
        if default is not None:
            return default
        raise InterpolationError(key, f"referenced key '{ref_key}' not found and no default provided")

    result = _INTERP_RE.sub(_replacer, raw)
    visiting.discard(key)
    resolved[key] = result
    return result


def interpolate(env: Dict[str, str]) -> InterpolationResult:
    """Resolve all variable references in *env* and return an InterpolationResult.

    Keys whose values contain no references are passed through unchanged.
    Keys that reference undefined variables (without defaults) are listed in
    ``result.unresolved``.  Keys involved in circular references are listed in
    ``result.cycles``.
    """
    result = InterpolationResult()
    resolved: Dict[str, str] = {}

    for key in env:
        try:
            result.resolved[key] = _resolve_value(key, env, resolved, set())
        except InterpolationError as exc:
            if "cycle" in exc.message or "self-reference" in exc.message:
                result.cycles.append(key)
            else:
                result.unresolved.append(key)
            # Fall back to the raw value so other keys can still resolve.
            result.resolved[key] = env[key]
        except KeyError as exc:
            result.unresolved.append(key)
            result.resolved[key] = env[key]

    return result


def interpolate_text(text: str) -> Tuple[str, InterpolationResult]:
    """Parse *text* as a .env file, interpolate references, and return the
    re-serialised text together with an InterpolationResult.

    Lines that are comments or blank are preserved verbatim.
    """
    env: Dict[str, str] = {}
    lines: List[str] = text.splitlines()
    pairs: List[Optional[Tuple[str, str]]] = []  # (key, raw_value) or None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            pairs.append(None)
            continue
        if "=" in stripped:
            k, _, v = stripped.partition("=")
            k = k.strip()
            v = v.strip()
            env[k] = v
            pairs.append((k, v))
        else:
            pairs.append(None)

    result = interpolate(env)

    out_lines: List[str] = []
    for line, pair in zip(lines, pairs):
        if pair is None:
            out_lines.append(line)
        else:
            k, _ = pair
            out_lines.append(f"{k}={result.resolved.get(k, env[k])}")

    return "\n".join(out_lines), result
