"""Detect dependencies between env keys (e.g. KEY_URL references KEY_HOST)."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

from envault.vault import load_manifest, _vault_path
from envault.crypto import decrypt_file


@dataclass
class DepGraph:
    edges: Dict[str, Set[str]] = field(default_factory=dict)  # key -> keys it references

    def add(self, src: str, dst: str) -> None:
        self.edges.setdefault(src, set()).add(dst)

    def dependents_of(self, key: str) -> Set[str]:
        """Return all keys that reference *key*."""
        return {src for src, dsts in self.edges.items() if key in dsts}

    def dependencies_of(self, key: str) -> Set[str]:
        return self.edges.get(key, set())


_REF_RE = re.compile(r'\$\{?([A-Z_][A-Z0-9_]*)\}?')


def parse_deps(env_text: str) -> DepGraph:
    """Build a dependency graph from env file content."""
    graph = DepGraph()
    for line in env_text.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        for ref in _REF_RE.findall(value):
            if ref != key:
                graph.add(key, ref)
    return graph


def deps_for_version(vault_dir: str, version: int, password: str) -> DepGraph:
    manifest = load_manifest(vault_dir)
    versions = manifest.get('versions', [])
    matches = [v for v in versions if v['version'] == version]
    if not matches:
        raise ValueError(f'Version {version} not found')
    enc_path = _vault_path(vault_dir) / matches[0]['file']
    plaintext = decrypt_file(str(enc_path), password)
    return parse_deps(plaintext.decode())


def format_graph(graph: DepGraph) -> str:
    if not graph.edges:
        return '(no dependencies found)'
    lines = []
    for src in sorted(graph.edges):
        dsts = ', '.join(sorted(graph.edges[src]))
        lines.append(f'  {src} -> {dsts}')
    return '\n'.join(lines)
