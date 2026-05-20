"""Compute similarity between two .env versions based on key/value overlap."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SimilarityResult:
    version_a: int
    version_b: int
    common_keys: List[str] = field(default_factory=list)
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    changed_keys: List[str] = field(default_factory=list)
    key_similarity: float = 0.0
    value_similarity: float = 0.0

    def __str__(self) -> str:
        return (
            f"Versions {self.version_a} vs {self.version_b}\n"
            f"  Key similarity  : {self.key_similarity:.1%}\n"
            f"  Value similarity: {self.value_similarity:.1%}\n"
            f"  Common keys     : {len(self.common_keys)}\n"
            f"  Only in v{self.version_a}    : {len(self.only_in_a)}\n"
            f"  Only in v{self.version_b}    : {len(self.only_in_b)}\n"
            f"  Changed values  : {len(self.changed_keys)}"
        )


def compare_dicts(
    a: Dict[str, str],
    b: Dict[str, str],
    version_a: int = 0,
    version_b: int = 1,
) -> SimilarityResult:
    """Return a SimilarityResult comparing two env dicts."""
    keys_a = set(a)
    keys_b = set(b)
    common = sorted(keys_a & keys_b)
    only_a = sorted(keys_a - keys_b)
    only_b = sorted(keys_b - keys_a)
    changed = [k for k in common if a[k] != b[k]]

    total_keys = len(keys_a | keys_b)
    key_sim = len(common) / total_keys if total_keys else 1.0

    unchanged = len(common) - len(changed)
    value_sim = unchanged / total_keys if total_keys else 1.0

    return SimilarityResult(
        version_a=version_a,
        version_b=version_b,
        common_keys=common,
        only_in_a=only_a,
        only_in_b=only_b,
        changed_keys=changed,
        key_similarity=key_sim,
        value_similarity=value_sim,
    )


def similarity_score(result: SimilarityResult) -> float:
    """Return a single 0-1 score averaging key and value similarity."""
    return (result.key_similarity + result.value_similarity) / 2.0
