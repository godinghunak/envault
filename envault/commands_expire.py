"""CLI commands for version expiry management."""

import argparse
import time
from envault.env_expire import (
    set_expiry, get_expiry, is_expired, list_expired, clear_expiry
)


def cmd_expire_set(args: argparse.Namespace) -> None:
    expires_at = set_expiry(args.vault_dir, args.version, args.ttl)
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expires_at))
    print(f"Version {args.version} will expire at {ts} (TTL={args.ttl}s)")


def cmd_expire_show(args: argparse.Namespace) -> None:
    exp = get_expiry(args.vault_dir, args.version)
    if exp is None:
        print(f"Version {args.version} has no expiry set")
        return
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(exp))
    expired = is_expired(args.vault_dir, args.version)
    status = "EXPIRED" if expired else "active"
    print(f"Version {args.version}: expires {ts} [{status}]")


def cmd_expire_list(args: argparse.Namespace) -> None:
    expired = list_expired(args.vault_dir)
    if not expired:
        print("No expired versions.")
        return
    print("Expired versions:")
    for v in sorted(expired):
        print(f"  v{v}")


def cmd_expire_clear(args: argparse.Namespace) -> None:
    removed = clear_expiry(args.vault_dir, args.version)
    if removed:
        print(f"Expiry cleared for version {args.version}")
    else:
        print(f"No expiry set for version {args.version}")


def register(subparsers, parent_parser) -> None:
    p = subparsers.add_parser("expire", help="Manage version expiry")
    sp = p.add_subparsers(dest="expire_cmd")

    s = sp.add_parser("set", parents=[parent_parser])
    s.add_argument("version", type=int)
    s.add_argument("ttl", type=int, help="TTL in seconds")
    s.set_defaults(func=cmd_expire_set)

    sh = sp.add_parser("show", parents=[parent_parser])
    sh.add_argument("version", type=int)
    sh.set_defaults(func=cmd_expire_show)

    ls = sp.add_parser("list", parents=[parent_parser])
    ls.set_defaults(func=cmd_expire_list)

    cl = sp.add_parser("clear", parents=[parent_parser])
    cl.add_argument("version", type=int)
    cl.set_defaults(func=cmd_expire_clear)
