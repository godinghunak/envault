"""CLI commands for lock file management."""
from __future__ import annotations
import argparse
from envault.env_lock import write_lock, read_lock, verify_lock


def cmd_lock_write(args: argparse.Namespace) -> None:
    version = getattr(args, "version", None)
    try:
        lock = write_lock(args.vault_dir, version=version)
        print(f"Lock written: version={lock['version']}, keys={len(lock['keys'])}, checksum={lock['checksum'][:12]}...")
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")


def cmd_lock_show(args: argparse.Namespace) -> None:
    try:
        lock = read_lock(args.vault_dir)
        print(f"Locked version : {lock['version']}")
        print(f"Checksum       : {lock['checksum']}")
        print(f"Keys ({len(lock['keys'])})      : {', '.join(lock['keys'])}")
    except FileNotFoundError as e:
        print(f"Error: {e}")


def cmd_lock_verify(args: argparse.Namespace) -> None:
    try:
        ok = verify_lock(args.vault_dir, args.password)
        if ok:
            print("Lock verified: environment matches locked version.")
        else:
            print("WARNING: Environment does NOT match locked version!")
    except FileNotFoundError as e:
        print(f"Error: {e}")


def register(subparsers: argparse._SubParsersAction) -> None:
    lock_p = subparsers.add_parser("lock", help="Manage envault lock file")
    lock_sub = lock_p.add_subparsers(dest="lock_cmd")

    wp = lock_sub.add_parser("write", help="Write lock file from current/specified version")
    wp.add_argument("--version", type=int, default=None)
    wp.set_defaults(func=cmd_lock_write)

    sp = lock_sub.add_parser("show", help="Show lock file contents")
    sp.set_defaults(func=cmd_lock_show)

    vp = lock_sub.add_parser("verify", help="Verify current version matches lock")
    vp.add_argument("--password", required=True)
    vp.set_defaults(func=cmd_lock_verify)
