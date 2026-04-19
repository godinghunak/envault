"""Summarize vault contents: key counts, version stats, profile/tag overview."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict

from envault.vault import load_manifest, list_versions
from envault.tags import load_tags
from envault.profiles import load_profiles
from envault.crypto import decrypt_file


@dataclass
class VaultSummary:
    total_versions: int = 0
    latest_version: int = 0
    total_keys: int = 0
    key_names: List[str] = field(default_factory=list)
    tags: Dict[str, int] = field(default_factory=dict)
    profiles: List[str] = field(default_factory=list)


def summarize(vault_dir: str, password: str) -> VaultSummary:
    """Build a VaultSummary for the given vault."""
    versions = list_versions(vault_dir)
    summary = VaultSummary(total_versions=len(versions))

    if versions:
        summary.latest_version = max(versions)
        try:
            content = decrypt_file(vault_dir, summary.latest_version, password)
            keys = [
                line.split("=", 1)[0].strip()
                for line in content.splitlines()
                if line.strip() and not line.startswith("#") and "=" in line
            ]
            summary.key_names = keys
            summary.total_keys = len(keys)
        except Exception:
            pass

    tags = load_tags(vault_dir)
    summary.tags = {name: ver for name, ver in tags.items()}

    profiles = load_profiles(vault_dir)
    summary.profiles = list(profiles.keys())

    return summary


def format_summary(s: VaultSummary) -> str:
    lines = [
        f"Versions  : {s.total_versions}",
        f"Latest    : {s.latest_version if s.total_versions else 'n/a'}",
        f"Keys      : {s.total_keys}",
    ]
    if s.key_names:
        lines.append("Key names : " + ", ".join(s.key_names))
    if s.tags:
        tag_str = ", ".join(f"{k}=v{v}" for k, v in s.tags.items())
        lines.append(f"Tags      : {tag_str}")
    else:
        lines.append("Tags      : (none)")
    if s.profiles:
        lines.append("Profiles  : " + ", ".join(s.profiles))
    else:
        lines.append("Profiles  : (none)")
    return "\n".join(lines)
