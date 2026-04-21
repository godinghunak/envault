"""CLI commands for namespace management."""
from __future__ import annotations

import argparse

from envault.env_namespace import (
    add_namespace,
    remove_namespace,
    list_namespaces,
    keys_in_namespace,
    resolve_namespace,
    load_namespaces,
)
from envault.export import export_latest
from envault.diff import parse_env


def cmd_namespace_add(args: argparse.Namespace) -> None:
    try:
        add_namespace(args.vault_dir, args.name, args.prefix)
        print(f"Namespace '{args.name}' -> prefix '{args.prefix.upper()}' added.")
    except (ValueError, KeyError) as exc:
        print(f"Error: {exc}")


def cmd_namespace_remove(args: argparse.Namespace) -> None:
    try:
        remove_namespace(args.vault_dir, args.name)
        print(f"Namespace '{args.name}' removed.")
    except KeyError as exc:
        print(f"Error: {exc}")


def cmd_namespace_list(args: argparse.Namespace) -> None:
    ns = load_namespaces(args.vault_dir)
    if not ns:
        print("No namespaces defined.")
        return
    for name, prefix in sorted(ns.items()):
        print(f"  {name}: {prefix}")


def cmd_namespace_show(args: argparse.Namespace) -> None:
    prefix = resolve_namespace(args.vault_dir, args.name)
    if prefix is None:
        print(f"Namespace '{args.name}' not found.")
        return
    try:
        content = export_latest(args.vault_dir, args.password)
    except Exception as exc:
        print(f"Error reading vault: {exc}")
        return
    env = parse_env(content)
    matched = keys_in_namespace(env, prefix)
    if not matched:
        print(f"No keys with prefix '{prefix}' found.")
        return
    for k, v in sorted(matched.items()):
        print(f"{k}={v}")


def register(subparsers: argparse.Action, parent: argparse.ArgumentParser) -> None:
    p = subparsers.add_parser("namespace", help="Manage key namespaces", parents=[parent])
    sub = p.add_subparsers(dest="ns_cmd", required=True)

    p_add = sub.add_parser("add", help="Add a namespace", parents=[parent])
    p_add.add_argument("name")
    p_add.add_argument("prefix")
    p_add.set_defaults(func=cmd_namespace_add)

    p_rm = sub.add_parser("remove", help="Remove a namespace", parents=[parent])
    p_rm.add_argument("name")
    p_rm.set_defaults(func=cmd_namespace_remove)

    p_ls = sub.add_parser("list", help="List namespaces", parents=[parent])
    p_ls.set_defaults(func=cmd_namespace_list)

    p_show = sub.add_parser("show", help="Show keys in namespace", parents=[parent])
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_namespace_show)
