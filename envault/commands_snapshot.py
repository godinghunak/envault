"""CLI commands for snapshot management."""
from __future__ import annotations
import argparse
from envault.env_snapshot import (
    create_snapshot, get_snapshot, delete_snapshot, list_snapshots
)


def cmd_snapshot_create(args: argparse.Namespace) -> None:
    version = getattr(args, "version", None)
    captured = create_snapshot(args.vault_dir, args.name, args.password, version)
    print(f"Snapshot '{args.name}' created from version {captured}.")


def cmd_snapshot_show(args: argparse.Namespace) -> None:
    snap = get_snapshot(args.vault_dir, args.name)
    print(f"Snapshot : {args.name}")
    print(f"Version  : {snap['version']}")
    print(f"Created  : {snap['created_at']}")
    print("Content  :")
    print(snap["content"])


def cmd_snapshot_delete(args: argparse.Namespace) -> None:
    delete_snapshot(args.vault_dir, args.name)
    print(f"Snapshot '{args.name}' deleted.")


def cmd_snapshot_list(args: argparse.Namespace) -> None:
    names = list_snapshots(args.vault_dir)
    if not names:
        print("No snapshots found.")
    else:
        for name in names:
            print(name)


def register(subparsers, parent_parser) -> None:
    p = subparsers.add_parser("snapshot", help="Manage named snapshots")
    sp = p.add_subparsers(dest="snapshot_cmd")

    c = sp.add_parser("create", help="Create a snapshot")
    c.add_argument("name")
    c.add_argument("--version", type=int, default=None)
    c.set_defaults(func=cmd_snapshot_create)

    s = sp.add_parser("show", help="Show snapshot content")
    s.add_argument("name")
    s.set_defaults(func=cmd_snapshot_show)

    d = sp.add_parser("delete", help="Delete a snapshot")
    d.add_argument("name")
    d.set_defaults(func=cmd_snapshot_delete)

    ls = sp.add_parser("list", help="List all snapshots")
    ls.set_defaults(func=cmd_snapshot_list)
