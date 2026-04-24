"""Key/value transformation rules for .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformRule:
    name: str
    description: str
    fn: Callable[[str, str], tuple[str, str]]


# Built-in transforms
def _uppercase_keys(k: str, v: str) -> tuple[str, str]:
    return k.upper(), v


def _lowercase_values(k: str, v: str) -> tuple[str, str]:
    return k, v.lower()


def _strip_quotes(k: str, v: str) -> tuple[str, str]:
    stripped = v.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in ('"', "'"):
        return k, stripped[1:-1]
    return k, v


def _trim_whitespace(k: str, v: str) -> tuple[str, str]:
    return k.strip(), v.strip()


BUILTIN_TRANSFORMS: Dict[str, TransformRule] = {
    "uppercase_keys": TransformRule(
        name="uppercase_keys",
        description="Convert all keys to uppercase",
        fn=_uppercase_keys,
    ),
    "lowercase_values": TransformRule(
        name="lowercase_values",
        description="Convert all values to lowercase",
        fn=_lowercase_values,
    ),
    "strip_quotes": TransformRule(
        name="strip_quotes",
        description="Remove surrounding quotes from values",
        fn=_strip_quotes,
    ),
    "trim_whitespace": TransformRule(
        name="trim_whitespace",
        description="Trim leading/trailing whitespace from keys and values",
        fn=_trim_whitespace,
    ),
}


@dataclass
class TransformResult:
    original: Dict[str, str]
    transformed: Dict[str, str]
    applied: List[str] = field(default_factory=list)

    @property
    def changed_keys(self) -> List[str]:
        changed = []
        for k, v in self.transformed.items():
            orig_v = self.original.get(k)
            if orig_v != v or k not in self.original:
                changed.append(k)
        return changed


def apply_transforms(
    env: Dict[str, str],
    transform_names: List[str],
) -> TransformResult:
    """Apply a sequence of named transforms to an env dict."""
    result = dict(env)
    applied = []
    for name in transform_names:
        rule = BUILTIN_TRANSFORMS.get(name)
        if rule is None:
            raise ValueError(f"Unknown transform: {name!r}")
        new_result: Dict[str, str] = {}
        for k, v in result.items():
            nk, nv = rule.fn(k, v)
            new_result[nk] = nv
        result = new_result
        applied.append(name)
    return TransformResult(original=dict(env), transformed=result, applied=applied)


def list_transforms() -> List[TransformRule]:
    return list(BUILTIN_TRANSFORMS.values())
