"""Environment inheritance: layer a child env on top of a parent env."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InheritanceResult:
    merged: Dict[str, str]
    overridden: List[str] = field(default_factory=list)   # keys child overrides
    inherited: List[str] = field(default_factory=list)    # keys taken from parent
    child_only: List[str] = field(default_factory=list)   # keys only in child

    def summary(self) -> str:
        lines = [
            f"Merged keys  : {len(self.merged)}",
            f"Inherited    : {len(self.inherited)}",
            f"Overridden   : {len(self.overridden)}",
            f"Child-only   : {len(self.child_only)}",
        ]
        return "\n".join(lines)


def inherit_dicts(
    parent: Dict[str, str],
    child: Dict[str, str],
    exclude: Optional[List[str]] = None,
) -> InheritanceResult:
    """Merge *child* on top of *parent*.

    Keys listed in *exclude* are not inherited from the parent.
    """
    exclude_set = set(exclude or [])
    merged: Dict[str, str] = {}
    overridden: List[str] = []
    inherited: List[str] = []
    child_only: List[str] = []

    for key, value in parent.items():
        if key in exclude_set:
            continue
        if key in child:
            merged[key] = child[key]
            overridden.append(key)
        else:
            merged[key] = value
            inherited.append(key)

    for key, value in child.items():
        if key not in merged:
            merged[key] = value
            child_only.append(key)

    return InheritanceResult(
        merged=merged,
        overridden=sorted(overridden),
        inherited=sorted(inherited),
        child_only=sorted(child_only),
    )


def inherit_versions(
    vault_dir: str,
    password: str,
    parent_version: int,
    child_version: int,
    exclude: Optional[List[str]] = None,
) -> InheritanceResult:
    """Load two vault versions and produce an inheritance result."""
    from envault.export import export_version
    from envault.diff import parse_env

    parent_text = export_version(vault_dir, password, parent_version)
    child_text = export_version(vault_dir, password, child_version)
    return inherit_dicts(parse_env(parent_text), parse_env(child_text), exclude=exclude)
