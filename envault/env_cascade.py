"""Cascade support: merge multiple env versions/profiles in priority order."""
from typing import List, Dict, Tuple
from envault.vault import load_manifest
from envault.export import export_version
from envault.diff import parse_env


class CascadeResult:
    def __init__(self, merged: Dict[str, str], sources: Dict[str, str]):
        self.merged = merged
        # sources maps key -> label indicating which layer provided the value
        self.sources = sources

    def __repr__(self) -> str:
        return f"CascadeResult(keys={list(self.merged.keys())})"


def cascade_dicts(
    layers: List[Tuple[str, Dict[str, str]]]
) -> CascadeResult:
    """Merge a list of (label, env_dict) layers, later layers take priority."""
    merged: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    for label, env in layers:
        for key, value in env.items():
            merged[key] = value
            sources[key] = label
    return CascadeResult(merged=merged, sources=sources)


def cascade_versions(
    vault_dir: str,
    password: str,
    version_labels: List[Tuple[str, int]],
) -> CascadeResult:
    """Cascade specific vault versions. version_labels is [(label, version), ...]."""
    layers = []
    for label, version in version_labels:
        plaintext = export_version(vault_dir, password, version)
        env_dict = parse_env(plaintext)
        layers.append((label, env_dict))
    return cascade_dicts(layers)


def format_cascade(result: CascadeResult, show_sources: bool = False) -> str:
    """Format a CascadeResult as env-file text, optionally annotating sources."""
    lines = []
    for key, value in sorted(result.merged.items()):
        if show_sources:
            lines.append(f"# source: {result.sources[key]}")
        lines.append(f"{key}={value}")
    return "\n".join(lines)
