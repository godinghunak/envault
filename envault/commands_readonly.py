"""CLI commands for read-only key protection."""

import argparse
from envault.env_readonly import (
    protect_key,
    unprotect_key,
    list_protected,
    is_protected,
    load_readonly,
)


def cmd_readonly_add(args: argparse.Namespace) -> None:
    reason = getattr(args, "reason", "") or ""
    try:
        protect_key(args.vault_dir, args.key, reason)
        print(f"Key '{args.key}' is now protected as read-only.")
        if reason:
            print(f"  Reason: {reason}")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_readonly_remove(args: argparse.Namespace) -> None:
    try:
        unprotect_key(args.vault_dir, args.key)
        print(f"Read-only protection removed from '{args.key}'.")
    except KeyError as e:
        print(f"Error: {e}")


def cmd_readonly_list(args: argparse.Namespace) -> None:
    data = load_readonly(args.vault_dir)
    keys = sorted(data.keys())
    if not keys:
        print("No read-only keys defined.")
        return
    print(f"{'Key':<30}  Reason")
    print("-" * 50)
    for key in keys:
        reason = data[key] or "(no reason)"
        print(f"{key:<30}  {reason}")


def cmd_readonly_check(args: argparse.Namespace) -> None:
    key = args.key
    protected = is_protected(args.vault_dir, key)
    if protected:
        data = load_readonly(args.vault_dir)
        reason = data[key] or "(no reason)"
        print(f"Key '{key}' is read-only. Reason: {reason}")
    else:
        print(f"Key '{key}' is not protected.")


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("readonly", help="Manage read-only key protections")
    sub = p.add_subparsers(dest="readonly_cmd", required=True)

    p_add = sub.add_parser("add", help="Protect a key as read-only")
    p_add.add_argument("key", help="Key name to protect")
    p_add.add_argument("--reason", default="", help="Reason for protection")
    p_add.set_defaults(func=cmd_readonly_add)

    p_rm = sub.add_parser("remove", help="Remove read-only protection")
    p_rm.add_argument("key", help="Key name to unprotect")
    p_rm.set_defaults(func=cmd_readonly_remove)

    p_ls = sub.add_parser("list", help="List all protected keys")
    p_ls.set_defaults(func=cmd_readonly_list)

    p_chk = sub.add_parser("check", help="Check if a key is protected")
    p_chk.add_argument("key", help="Key name to check")
    p_chk.set_defaults(func=cmd_readonly_check)
