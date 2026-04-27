"""CLI command for cross-referencing keys between two vault versions."""
from __future__ import annotations
import argparse
import sys

from envault.env_crossref import crossref_versions, format_crossref
from envault.vault import load_manifest


def cmd_crossref(args: argparse.Namespace) -> None:
    manifest = load_manifest(args.vault_dir)
    versions = manifest.get("versions", [])

    if len(versions) < 2:
        print("At least two versions are required for cross-reference comparison.")
        sys.exit(1)

    version_a = args.version_a
    version_b = args.version_b

    available = [v["version"] for v in versions]

    if version_a not in available:
        print(f"Version {version_a} not found in vault.")
        sys.exit(1)

    if version_b not in available:
        print(f"Version {version_b} not found in vault.")
        sys.exit(1)

    result = crossref_versions(
        vault_dir=args.vault_dir,
        password=args.password,
        version_a=version_a,
        version_b=version_b,
    )

    print(format_crossref(result))

    if not result.ok and getattr(args, "strict", False):
        sys.exit(1)


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "crossref",
        help="Find keys present in one version but missing in another",
    )
    p.add_argument("version_a", type=int, help="First version number")
    p.add_argument("version_b", type=int, help="Second version number")
    p.add_argument("--password", required=True, help="Vault password")
    p.add_argument("--vault-dir", default=".envault", dest="vault_dir")
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any issues are found",
    )
    p.set_defaults(func=cmd_crossref)
