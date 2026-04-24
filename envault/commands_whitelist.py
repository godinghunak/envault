"""CLI commands for whitelist management."""

from __future__ import annotations

from envault.env_whitelist import (
    add_key,
    check_env,
    load_whitelist,
    remove_key,
)
from envault.vault import load_manifest
from envault.export import export_latest
from envault.diff import parse_env


def _latest_env(vault_dir: str, password: str) -> dict:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        return {}
    plaintext = export_latest(vault_dir, password)
    return parse_env(plaintext)


def cmd_whitelist_add(args) -> None:
    key = args.key.strip().upper()
    try:
        add_key(args.vault_dir, key)
        print(f"Added '{key}' to whitelist.")
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_whitelist_remove(args) -> None:
    key = args.key.strip().upper()
    removed = remove_key(args.vault_dir, key)
    if removed:
        print(f"Removed '{key}' from whitelist.")
    else:
        print(f"Key '{key}' was not in the whitelist.")


def cmd_whitelist_list(args) -> None:
    keys = load_whitelist(args.vault_dir)
    if not keys:
        print("Whitelist is empty (all keys allowed).")
    else:
        print("Allowed keys:")
        for k in keys:
            print(f"  {k}")


def cmd_whitelist_check(args) -> None:
    env = _latest_env(args.vault_dir, args.password)
    violations = check_env(args.vault_dir, env)
    if not violations:
        print("OK — all keys are whitelisted.")
    else:
        print(f"{len(violations)} violation(s) found:")
        for v in violations:
            print(f"  {v}")


def register(subparsers) -> None:
    p = subparsers.add_parser("whitelist", help="Manage key whitelist")
    sp = p.add_subparsers(dest="whitelist_cmd", required=True)

    add_p = sp.add_parser("add", help="Add a key to the whitelist")
    add_p.add_argument("key")
    add_p.set_defaults(func=cmd_whitelist_add)

    rm_p = sp.add_parser("remove", help="Remove a key from the whitelist")
    rm_p.add_argument("key")
    rm_p.set_defaults(func=cmd_whitelist_remove)

    ls_p = sp.add_parser("list", help="List whitelisted keys")
    ls_p.set_defaults(func=cmd_whitelist_list)

    chk_p = sp.add_parser("check", help="Check latest version against whitelist")
    chk_p.add_argument("--password", default="")
    chk_p.set_defaults(func=cmd_whitelist_check)
