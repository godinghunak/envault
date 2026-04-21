"""Variable substitution: resolve ${VAR} references within .env values."""

import re
from typing import Dict, List, Optional

_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class SubstitutionError(Exception):
    """Raised when a variable reference cannot be resolved."""

    def __init__(self, key: str, ref: str):
        self.key = key
        self.ref = ref
        super().__init__(f"Key '{key}' references undefined variable '${{{ref}}}'")


def find_references(value: str) -> List[str]:
    """Return all variable names referenced in *value* via ${NAME} syntax."""
    return _REF_RE.findall(value)


def substitute(value: str, env: Dict[str, str], key: str = "?") -> str:
    """Replace all ${VAR} placeholders in *value* using *env*.

    Raises SubstitutionError if a referenced variable is absent.
    """
    def _replace(m: re.Match) -> str:
        ref = m.group(1)
        if ref not in env:
            raise SubstitutionError(key, ref)
        return env[ref]

    return _REF_RE.sub(_replace, value)


def resolve_env(env: Dict[str, str], *, strict: bool = True) -> Dict[str, str]:
    """Return a new dict with all ${VAR} references expanded.

    Resolution is done in iteration order; forward references are supported
    because each key is resolved against the *original* env.

    If *strict* is False, unresolvable references are left as-is instead of
    raising an error.
    """
    resolved: Dict[str, str] = {}
    for k, v in env.items():
        if not find_references(v):
            resolved[k] = v
            continue
        try:
            resolved[k] = substitute(v, env, key=k)
        except SubstitutionError:
            if strict:
                raise
            resolved[k] = v
    return resolved


def find_unresolved(env: Dict[str, str]) -> List[str]:
    """Return keys whose values contain references to undefined variables."""
    bad: List[str] = []
    for k, v in env.items():
        for ref in find_references(v):
            if ref not in env:
                bad.append(k)
                break
    return bad
