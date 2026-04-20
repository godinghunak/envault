"""CLI commands for env variable grouping."""

from __future__ import annotations

import argparse

from envault.env_group import (
    format_groups,
    get_group,
    group_by_custom,
    group_by_prefix,
    list_groups,
)
from envault.export import export_latest, export_version
from envault.diff import parse_env


def _load_env(args: argparse.Namespace) -> dict:
    version = getattr(args, "version", None)
    if version is not None:
        raw = export_version(args.vault_dir, args.password, int(version))
    else:
        raw = export_latest(args.vault_dir, args.password)
    return parse_env(raw)


def cmd_group(args: argparse.Namespace) -> None:
    """Group env vars by prefix and display them."""
    env = _load_env(args)
    separator = getattr(args, "separator", "_") or "_"
    grouped = group_by_prefix(env, separator=separator)

    target = getattr(args, "group", None)
    if target:
        members = get_group(grouped, target)
        if members is None:
            print(f"Group '{target}' not found.")
            return
        for key, value in sorted(members.items()):
            print(f"{key}={value}")
    else:
        names = list_groups(grouped)
        if not names:
            print("No groups found.")
            return
        print(format_groups(grouped))


def register(subparsers) -> None:
    p = subparsers.add_parser("group", help="Group env vars by prefix")
    p.add_argument("vault_dir", help="Path to the vault directory")
    p.add_argument("password", help="Vault password")
    p.add_argument("--version", "-v", default=None, help="Version number (default: latest)")
    p.add_argument("--separator", "-s", default="_", help="Key separator (default: _)")
    p.add_argument("--group", "-g", default=None, help="Show only this group")
    p.set_defaults(func=cmd_group)
