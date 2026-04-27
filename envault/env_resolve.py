"""Resolve environment variable references across versions or profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ResolutionError:
    key: str
    reason: str

    def __str__(self) -> str:
        return f"Cannot resolve '{self.key}': {self.reason}"


@dataclass
class ResolveResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    errors: List[ResolutionError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def __repr__(self) -> str:
        return f"<ResolveResult resolved={len(self.resolved)} errors={len(self.errors)}>"


def resolve_references(
    base: Dict[str, str],
    overrides: Optional[Dict[str, str]] = None,
    strict: bool = False,
) -> ResolveResult:
    """Merge base with overrides, resolving ${VAR} references in values."""
    merged = {**base, **(overrides or {})}
    result = ResolveResult()

    for key, value in merged.items():
        try:
            resolved = _expand(value, merged)
            result.resolved[key] = resolved
        except KeyError as exc:
            missing = str(exc).strip("'")
            err = ResolutionError(key=key, reason=f"undefined reference ${{{missing}}}")
            result.errors.append(err)
            if strict:
                raise ValueError(str(err)) from exc
            result.resolved[key] = value

    return result


def _expand(value: str, env: Dict[str, str], depth: int = 0) -> str:
    """Recursively expand ${VAR} references up to a fixed depth."""
    if depth > 10:
        return value
    import re
    pattern = re.compile(r"\$\{([^}]+)\}")
    def replacer(m: re.Match) -> str:
        ref = m.group(1)
        if ref not in env:
            raise KeyError(ref)
        return _expand(env[ref], env, depth + 1)
    return pattern.sub(replacer, value)


def format_resolve_result(result: ResolveResult) -> str:
    lines = []
    for key, val in sorted(result.resolved.items()):
        lines.append(f"{key}={val}")
    if result.errors:
        lines.append("")
        lines.append("Errors:")
        for err in result.errors:
            lines.append(f"  {err}")
    return "\n".join(lines)
