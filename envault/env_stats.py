"""Statistics and analytics for vault versions."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

from envault.vault import load_manifest
from envault.export import export_version
from envault.diff import parse_env, diff_envs


@dataclass
class VaultStats:
    total_versions: int = 0
    total_keys: int = 0
    unique_keys: int = 0
    avg_keys_per_version: float = 0.0
    most_changed_keys: List[str] = field(default_factory=list)
    key_frequency: Dict[str, int] = field(default_factory=dict)


def _key_frequency(vault_dir: str, password: str) -> Dict[str, int]:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    freq: Dict[str, int] = {}
    for v in versions:
        try:
            content = export_version(vault_dir, v["version"], password)
            for key in parse_env(content):
                freq[key] = freq.get(key, 0) + 1
        except Exception:
            continue
    return freq


def compute_stats(vault_dir: str, password: str) -> VaultStats:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    stats = VaultStats(total_versions=len(versions))

    if not versions:
        return stats

    freq = _key_frequency(vault_dir, password)
    stats.key_frequency = freq
    stats.unique_keys = len(freq)
    stats.total_keys = sum(freq.values())
    stats.avg_keys_per_version = (
        stats.total_keys / stats.total_versions if stats.total_versions else 0.0
    )

    # most changed = keys that appear in diffs most often
    change_count: Dict[str, int] = {}
    sorted_versions = sorted(versions, key=lambda v: v["version"])
    for i in range(1, len(sorted_versions)):
        try:
            prev = export_version(vault_dir, sorted_versions[i - 1]["version"], password)
            curr = export_version(vault_dir, sorted_versions[i]["version"], password)
            diff = diff_envs(parse_env(prev), parse_env(curr))
            for entry in diff:
                change_count[entry.key] = change_count.get(entry.key, 0) + 1
        except Exception:
            continue

    stats.most_changed_keys = sorted(change_count, key=lambda k: -change_count[k])[:5]
    return stats


def format_stats(stats: VaultStats) -> str:
    lines = [
        f"Total versions   : {stats.total_versions}",
        f"Unique keys      : {stats.unique_keys}",
        f"Avg keys/version : {stats.avg_keys_per_version:.1f}",
    ]
    if stats.most_changed_keys:
        lines.append("Most changed keys: " + ", ".join(stats.most_changed_keys))
    if stats.key_frequency:
        lines.append("Key frequency:")
        for k, v in sorted(stats.key_frequency.items(), key=lambda x: -x[1]):
            lines.append(f"  {k}: {v}")
    return "\n".join(lines)
