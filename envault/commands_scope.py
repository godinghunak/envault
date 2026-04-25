"""CLI commands for scope management."""
from __future__ import annotations

import argparse

from envault.env_scope import (
    add_scope,
    apply_scope,
    get_scope,
    list_scopes,
    remove_scope,
)
from envault.export import export_latest


def cmd_scope_add(args: argparse.Namespace) -> None:
    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    try:
        add_scope(args.vault_dir, args.name, keys)
        print(f"Scope '{args.name}' saved with {len(keys)} key(s).")
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_scope_remove(args: argparse.Namespace) -> None:
    try:
        remove_scope(args.vault_dir, args.name)
        print(f"Scope '{args.name}' removed.")
    except KeyError as exc:
        print(f"Error: {exc}")


def cmd_scope_list(args: argparse.Namespace) -> None:
    names = list_scopes(args.vault_dir)
    if not names:
        print("No scopes defined.")
        return
    scopes_data = {}
    from envault.env_scope import load_scopes
    all_scopes = load_scopes(args.vault_dir)
    for name in names:
        key_count = len(all_scopes[name])
        print(f"  {name}  ({key_count} key(s))")


def cmd_scope_show(args: argparse.Namespace) -> None:
    keys = get_scope(args.vault_dir, args.name)
    if keys is None:
        print(f"Scope '{args.name}' not found.")
        return
    print(f"Scope '{args.name}':")
    for k in sorted(keys):
        print(f"  {k}")


def cmd_scope_apply(args: argparse.Namespace) -> None:
    """Print the env filtered to only the keys in a scope."""
    keys = get_scope(args.vault_dir, args.name)
    if keys is None:
        print(f"Error: Scope '{args.name}' not found.")
        return
    try:
        content = export_latest(args.vault_dir, args.password)
    except Exception as exc:
        print(f"Error exporting vault: {exc}")
        return
    env: dict = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    filtered = apply_scope(env, keys)
    for k, v in sorted(filtered.items()):
        print(f"{k}={v}")


def register(subparsers: argparse._SubParsersAction, common_args) -> None:  # type: ignore
    p = subparsers.add_parser("scope", help="Manage key scopes")
    sp = p.add_subparsers(dest="scope_cmd")

    pa = sp.add_parser("add", help="Add or replace a scope")
    common_args(pa)
    pa.add_argument("name", help="Scope name")
    pa.add_argument("keys", help="Comma-separated list of keys")
    pa.set_defaults(func=cmd_scope_add)

    pr = sp.add_parser("remove", help="Remove a scope")
    common_args(pr)
    pr.add_argument("name", help="Scope name")
    pr.set_defaults(func=cmd_scope_remove)

    pl = sp.add_parser("list", help="List all scopes")
    common_args(pl)
    pl.set_defaults(func=cmd_scope_list)

    ps = sp.add_parser("show", help="Show keys in a scope")
    common_args(ps)
    ps.add_argument("name", help="Scope name")
    ps.set_defaults(func=cmd_scope_show)

    pap = sp.add_parser("apply", help="Print env filtered by scope")
    common_args(pap)
    pap.add_argument("name", help="Scope name")
    pap.set_defaults(func=cmd_scope_apply)
