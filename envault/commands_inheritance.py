"""CLI commands for env inheritance."""
from __future__ import annotations

import sys
from argparse import Namespace

from envault.env_inheritance import inherit_versions, inherit_dicts
from envault.export import export_version, export_latest
from envault.diff import parse_env
from envault.vault import load_manifest


def _latest_version(vault_dir: str) -> int:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        return 0
    return max(v["version"] for v in versions)


def cmd_inherit(args: Namespace) -> None:
    """Merge a child version on top of a parent version and print the result."""
    vault_dir: str = args.vault_dir
    password: str = args.password
    exclude = args.exclude or []

    parent_ver = args.parent
    child_ver = args.child if args.child is not None else _latest_version(vault_dir)

    if parent_ver == 0:
        print("Error: no versions in vault.", file=sys.stderr)
        sys.exit(1)

    try:
        result = inherit_versions(vault_dir, password, parent_ver, child_ver, exclude=exclude)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        print(result.summary())
        return

    for key, value in sorted(result.merged.items()):
        origin = "(parent)"
        if key in result.overridden:
            origin = "(overridden)"
        elif key in result.child_only:
            origin = "(child-only)"
        if args.verbose:
            print(f"{key}={value}  {origin}")
        else:
            print(f"{key}={value}")


def register(subparsers) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "inherit",
        help="Merge a parent env version under a child env version",
    )
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--password", required=True, help="Vault password")
    p.add_argument("--parent", type=int, required=True, help="Parent version number")
    p.add_argument("--child", type=int, default=None, help="Child version (default: latest)")
    p.add_argument(
        "--exclude",
        nargs="*",
        metavar="KEY",
        help="Keys to exclude from parent inheritance",
    )
    p.add_argument("--summary", action="store_true", help="Print summary only")
    p.add_argument("-v", "--verbose", action="store_true", help="Show key origin")
    p.set_defaults(func=cmd_inherit)
