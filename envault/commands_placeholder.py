"""CLI commands for placeholder detection."""

from __future__ import annotations
import argparse
from envault.vault import load_manifest
from envault.export import export_version, export_latest
from envault.env_placeholder import find_placeholders_in_text


def cmd_placeholder_check(args: argparse.Namespace) -> None:
    version = getattr(args, 'version', None)
    password = args.password
    vault_dir = args.vault_dir

    if version is None:
        manifest = load_manifest(vault_dir)
        versions = manifest.get('versions', [])
        if not versions:
            print('No versions found in vault.')
            return
        text = export_latest(vault_dir, password)
        label = f'latest (v{versions[-1]})'  
    else:
        text = export_version(vault_dir, version, password)
        label = f'v{version}'

    issues = find_placeholders_in_text(text)
    if not issues:
        print(f'No placeholders found in {label}.')
    else:
        print(f'Placeholders found in {label}:')
        for issue in issues:
            print(f'  {issue}')


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser('placeholder', help='Detect placeholder values in env versions')
    sub = p.add_subparsers(dest='placeholder_cmd')

    check = sub.add_parser('check', help='Check for placeholder values')
    check.add_argument('--version', type=int, default=None, help='Version to check (default: latest)')
    check.add_argument('--password', required=True, help='Vault password')
    check.set_defaults(func=cmd_placeholder_check)
