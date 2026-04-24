"""CLI commands for prefix operations on vault versions."""

from __future__ import annotations

import argparse
from typing import Optional

from envault.vault import load_manifest, _vault_path
from envault.crypto import decrypt_file, encrypt_file
from envault.diff import parse_env
from envault.env_prefix import (
    add_prefix,
    strip_prefix,
    replace_prefix,
    list_prefixes,
    diff_prefix_changes,
)


def _latest_version(vault_dir: str) -> Optional[int]:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    return max(versions) if versions else None


def _load_env(vault_dir: str, version: int, password: str) -> dict:
    path = _vault_path(vault_dir) / f"v{version}.env.enc"
    plaintext = decrypt_file(str(path), password)
    return parse_env(plaintext.decode())


def cmd_prefix(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    password = args.password
    version = args.version or _latest_version(vault_dir)
    if version is None:
        print("No versions found.")
        return

    env = _load_env(vault_dir, version, password)

    if args.prefix_action == "add":
        updated = add_prefix(env, args.prefix)
        changes = diff_prefix_changes(env, updated)
        for c in changes:
            print(f"  {c}")
        print(f"Added prefix '{args.prefix.upper()}' to {len(changes)} key(s).")

    elif args.prefix_action == "strip":
        updated = strip_prefix(env, args.prefix)
        changes = diff_prefix_changes(env, updated)
        for c in changes:
            print(f"  {c}")
        print(f"Stripped prefix '{args.prefix.upper()}' from {len(changes)} key(s).")

    elif args.prefix_action == "replace":
        updated = replace_prefix(env, args.old_prefix, args.new_prefix)
        changes = diff_prefix_changes(env, updated)
        for c in changes:
            print(f"  {c}")
        print(
            f"Replaced '{args.old_prefix.upper()}' with '{args.new_prefix.upper()}'"
            f" on {len(changes)} key(s)."
        )

    elif args.prefix_action == "list":
        prefixes = list_prefixes(env)
        if not prefixes:
            print("No prefixes found.")
        else:
            for p in prefixes:
                print(f"  {p}")


def register(subparsers) -> None:
    p = subparsers.add_parser("prefix", help="Manage key prefixes")
    p.add_argument("--vault-dir", default=".envault")
    p.add_argument("--password", required=True)
    p.add_argument("--version", type=int, default=None)
    sub = p.add_subparsers(dest="prefix_action", required=True)

    add_p = sub.add_parser("add", help="Add a prefix to all keys")
    add_p.add_argument("prefix")

    strip_p = sub.add_parser("strip", help="Strip a prefix from matching keys")
    strip_p.add_argument("prefix")

    rep_p = sub.add_parser("replace", help="Replace one prefix with another")
    rep_p.add_argument("old_prefix")
    rep_p.add_argument("new_prefix")

    sub.add_parser("list", help="List all key prefixes")

    p.set_defaults(func=cmd_prefix)
