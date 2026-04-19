"""CLI commands for env key dependency analysis."""
from __future__ import annotations
import argparse

from envault.vault import load_manifest
from envault.env_deps import deps_for_version, format_graph


def _latest_version(vault_dir: str) -> int:
    manifest = load_manifest(vault_dir)
    versions = manifest.get('versions', [])
    if not versions:
        raise ValueError('No versions in vault')
    return max(v['version'] for v in versions)


def cmd_deps(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    password = args.password

    version = getattr(args, 'version', None)
    if version is None:
        try:
            version = _latest_version(vault_dir)
        except ValueError as exc:
            print(f'Error: {exc}')
            return

    try:
        graph = deps_for_version(vault_dir, version, password)
    except ValueError as exc:
        print(f'Error: {exc}')
        return

    key = getattr(args, 'key', None)
    if key:
        deps = graph.dependencies_of(key)
        dependents = graph.dependents_of(key)
        if deps:
            print(f'{key} depends on: {", ".join(sorted(deps))}')
        else:
            print(f'{key} has no dependencies')
        if dependents:
            print(f'{key} is referenced by: {", ".join(sorted(dependents))}')
        else:
            print(f'{key} is not referenced by any key')
    else:
        print(f'Dependency graph for version {version}:')
        print(format_graph(graph))


def register(subparsers) -> None:
    p = subparsers.add_parser('deps', help='Show env key dependencies')
    p.add_argument('--vault-dir', default='.envault')
    p.add_argument('--password', required=True)
    p.add_argument('--version', type=int, default=None)
    p.add_argument('--key', default=None, help='Inspect a specific key')
    p.set_defaults(func=cmd_deps)
