"""Prefix management: add, strip, or replace key prefixes in env files."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PrefixChange:
    key: str
    old_key: str
    new_key: str
    value: str

    def __str__(self) -> str:
        return f"{self.old_key} -> {self.new_key}"


def add_prefix(env: Dict[str, str], prefix: str) -> Dict[str, str]:
    """Return a new dict with *prefix* prepended to every key."""
    prefix = prefix.upper()
    return {f"{prefix}{k}": v for k, v in env.items()}


def strip_prefix(env: Dict[str, str], prefix: str) -> Dict[str, str]:
    """Return a new dict with *prefix* removed from matching keys.

    Keys that do not start with *prefix* are left unchanged.
    """
    prefix = prefix.upper()
    result: Dict[str, str] = {}
    for k, v in env.items():
        if k.startswith(prefix):
            result[k[len(prefix):]] = v
        else:
            result[k] = v
    return result


def replace_prefix(
    env: Dict[str, str], old_prefix: str, new_prefix: str
) -> Dict[str, str]:
    """Replace *old_prefix* with *new_prefix* on matching keys."""
    old_prefix = old_prefix.upper()
    new_prefix = new_prefix.upper()
    result: Dict[str, str] = {}
    for k, v in env.items():
        if k.startswith(old_prefix):
            result[f"{new_prefix}{k[len(old_prefix):]}"] = v
        else:
            result[k] = v
    return result


def diff_prefix_changes(
    original: Dict[str, str], updated: Dict[str, str]
) -> List[PrefixChange]:
    """Return a list of PrefixChange objects describing key renames."""
    changes: List[PrefixChange] = []
    orig_vals = {v: k for k, v in original.items()}
    for new_key, val in updated.items():
        old_key = orig_vals.get(val)
        if old_key and old_key != new_key:
            changes.append(PrefixChange(key=new_key, old_key=old_key, new_key=new_key, value=val))
    return changes


def list_prefixes(env: Dict[str, str], separator: str = "_") -> List[str]:
    """Return sorted unique prefixes found in *env* keys."""
    prefixes: set = set()
    for k in env:
        if separator in k:
            prefixes.add(k.split(separator, 1)[0])
    return sorted(prefixes)
