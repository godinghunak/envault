"""CLI commands for version lineage inspection."""

from __future__ import annotations

import argparse
from typing import Optional

from envault.env_lineage import (
    ancestors,
    descendants,
    lineage_chain,
    load_lineage,
    record_version,
)


def _latest_version(vault_dir: str) -> Optional[int]:
    from envault.vault import load_manifest
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    return max(versions) if versions else None


def cmd_lineage_record(args: argparse.Namespace) -> None:
    """Record a parent->child relationship."""
    parent = args.parent if args.parent else None
    record_version(args.vault_dir, args.version, parent)
    if parent is None:
        print(f"Recorded version {args.version} as root.")
    else:
        print(f"Recorded version {args.version} (parent: {parent}).")


def cmd_lineage_ancestors(args: argparse.Namespace) -> None:
    version = args.version or _latest_version(args.vault_dir)
    if version is None:
        print("No versions found.")
        return
    chain = ancestors(args.vault_dir, version)
    if not chain:
        print(f"Version {version} has no recorded ancestors.")
    else:
        print(f"Ancestors of version {version}: " + " -> ".join(str(v) for v in chain))


def cmd_lineage_descendants(args: argparse.Namespace) -> None:
    version = args.version or _latest_version(args.vault_dir)
    if version is None:
        print("No versions found.")
        return
    desc = descendants(args.vault_dir, version)
    if not desc:
        print(f"Version {version} has no recorded descendants.")
    else:
        print(f"Descendants of version {version}: " + ", ".join(str(v) for v in desc))


def cmd_lineage_chain(args: argparse.Namespace) -> None:
    version = args.version or _latest_version(args.vault_dir)
    if version is None:
        print("No versions found.")
        return
    chain = lineage_chain(args.vault_dir, version)
    print(" -> ".join(str(v) for v in chain))


def cmd_lineage_show(args: argparse.Namespace) -> None:
    """Show the full lineage map."""
    lineage = load_lineage(args.vault_dir)
    if not lineage:
        print("No lineage recorded.")
        return
    for ver in sorted(lineage):
        parent = lineage[ver]
        parent_str = str(parent) if parent is not None else "(root)"
        print(f"  v{ver}  <-  {parent_str}")


def register(subparsers: argparse._SubParsersAction, vault_dir: str) -> None:
    p = subparsers.add_parser("lineage", help="Inspect version lineage")
    p.add_argument("--vault-dir", default=vault_dir)
    sub = p.add_subparsers(dest="lineage_cmd")

    rec = sub.add_parser("record", help="Record a version's parent")
    rec.add_argument("version", type=int)
    rec.add_argument("--parent", type=int, default=None)
    rec.set_defaults(func=cmd_lineage_record)

    anc = sub.add_parser("ancestors", help="Show ancestors of a version")
    anc.add_argument("version", type=int, nargs="?")
    anc.set_defaults(func=cmd_lineage_ancestors)

    des = sub.add_parser("descendants", help="Show descendants of a version")
    des.add_argument("version", type=int, nargs="?")
    des.set_defaults(func=cmd_lineage_descendants)

    ch = sub.add_parser("chain", help="Show full chain to a version")
    ch.add_argument("version", type=int, nargs="?")
    ch.set_defaults(func=cmd_lineage_chain)

    sh = sub.add_parser("show", help="Show full lineage map")
    sh.set_defaults(func=cmd_lineage_show)
