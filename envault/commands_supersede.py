"""commands_supersede.py – CLI commands for version supersede tracking."""
from __future__ import annotations

import sys
from typing import Any

from envault.env_supersede import (
    get_superseded_by,
    list_superseded,
    mark_superseded,
    unmark_superseded,
)
from envault.vault import load_manifest


def _latest_version(vault_dir: str) -> int:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        return 0
    return max(int(v["version"]) for v in versions)


def cmd_supersede_mark(args: Any) -> None:
    """Mark a version as superseded by another."""
    try:
        mark_superseded(args.vault_dir, int(args.version), int(args.superseded_by))
        print(f"Version {args.version} is now marked as superseded by {args.superseded_by}.")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_supersede_unmark(args: Any) -> None:
    """Remove the supersede record for a version."""
    unmark_superseded(args.vault_dir, int(args.version))
    print(f"Supersede record for version {args.version} removed.")


def cmd_supersede_show(args: Any) -> None:
    """Show what supersedes a given version."""
    result = get_superseded_by(args.vault_dir, int(args.version))
    if result is None:
        print(f"Version {args.version} has no supersede record.")
    else:
        print(f"Version {args.version} is superseded by version {result}.")


def cmd_supersede_list(args: Any) -> None:
    """List all supersede relationships."""
    entries = list_superseded(args.vault_dir)
    if not entries:
        print("No supersede records found.")
        return
    for entry in entries:
        print(f"  v{entry['version']} -> v{entry['superseded_by']}")


def register(subparsers: Any, vault_dir: str) -> None:
    p = subparsers.add_parser("supersede", help="Manage version supersede records")
    sp = p.add_subparsers(dest="supersede_cmd")

    m = sp.add_parser("mark", help="Mark version as superseded")
    m.add_argument("version", type=int)
    m.add_argument("superseded_by", type=int)
    m.set_defaults(func=cmd_supersede_mark, vault_dir=vault_dir)

    u = sp.add_parser("unmark", help="Remove supersede record")
    u.add_argument("version", type=int)
    u.set_defaults(func=cmd_supersede_unmark, vault_dir=vault_dir)

    s = sp.add_parser("show", help="Show supersede info for a version")
    s.add_argument("version", type=int)
    s.set_defaults(func=cmd_supersede_show, vault_dir=vault_dir)

    ls = sp.add_parser("list", help="List all supersede records")
    ls.set_defaults(func=cmd_supersede_list, vault_dir=vault_dir)
