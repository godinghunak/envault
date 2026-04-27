"""CLI commands for immutable version management."""

from __future__ import annotations

import argparse

from envault.env_immutable import (
    assert_mutable,
    is_immutable,
    list_immutable,
    load_immutable,
    lock_version,
    unlock_version,
)
from envault.vault import load_manifest


def _latest_version(vault_dir: str) -> int:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions found in vault.")
    return max(v["version"] for v in versions)


def cmd_immutable_lock(args: argparse.Namespace) -> None:
    version = args.version if args.version is not None else _latest_version(args.vault_dir)
    reason = args.reason or ""
    lock_version(args.vault_dir, version, reason)
    print(f"Version {version} locked as immutable." + (f" Reason: {reason}" if reason else ""))


def cmd_immutable_unlock(args: argparse.Namespace) -> None:
    version = args.version if args.version is not None else _latest_version(args.vault_dir)
    if not is_immutable(args.vault_dir, version):
        print(f"Version {version} is not immutable.")
        return
    unlock_version(args.vault_dir, version)
    print(f"Version {version} is now mutable.")


def cmd_immutable_list(args: argparse.Namespace) -> None:
    versions = list_immutable(args.vault_dir)
    if not versions:
        print("No immutable versions.")
        return
    records = load_immutable(args.vault_dir)
    for v in versions:
        reason = records[v]
        line = f"  v{v}"
        if reason:
            line += f" — {reason}"
        print(line)


def cmd_immutable_check(args: argparse.Namespace) -> None:
    version = args.version if args.version is not None else _latest_version(args.vault_dir)
    if is_immutable(args.vault_dir, version):
        records = load_immutable(args.vault_dir)
        reason = records[version]
        msg = f"Version {version} is IMMUTABLE"
        if reason:
            msg += f": {reason}"
        print(msg)
    else:
        print(f"Version {version} is mutable.")


def register(subparsers: argparse._SubParsersAction, global_vault_dir: str) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("immutable", help="Manage immutable version locks")
    sp = p.add_subparsers(dest="immutable_cmd")

    for name, fn, help_text in [
        ("lock", cmd_immutable_lock, "Lock a version as immutable"),
        ("unlock", cmd_immutable_unlock, "Remove immutable lock from a version"),
        ("list", cmd_immutable_list, "List all immutable versions"),
        ("check", cmd_immutable_check, "Check if a version is immutable"),
    ]:
        sub = sp.add_parser(name, help=help_text)
        sub.set_defaults(func=fn, vault_dir=global_vault_dir)
        if name in ("lock", "unlock", "check"):
            sub.add_argument("--version", type=int, default=None, help="Version number (default: latest)")
        if name == "lock":
            sub.add_argument("--reason", default="", help="Reason for locking")
