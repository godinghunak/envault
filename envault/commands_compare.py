"""CLI commands for env-compare feature."""
from __future__ import annotations
import argparse
from envault.env_compare import (
    compare_versions,
    compare_file_to_version,
    format_compare,
)


def cmd_compare(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    password = args.password

    if args.file:
        version = args.version_b if hasattr(args, "version_b") and args.version_b else None
        result = compare_file_to_version(vault_dir, password, args.file, version)
        label_a = args.file
        label_b = f"v{version}" if version else "latest"
    else:
        if args.version_a is None or args.version_b is None:
            print("Error: provide --version-a and --version-b, or --file.")
            return
        result = compare_versions(vault_dir, password, args.version_a, args.version_b)
        label_a = f"v{args.version_a}"
        label_b = f"v{args.version_b}"

    print(f"Comparing {label_a} vs {label_b}:")
    print(format_compare(result, label_a, label_b))
    if result.has_differences():
        print("\nDifferences found.")
    else:
        print("\nNo differences.")


def register(subparsers) -> None:
    p = subparsers.add_parser("compare", help="Compare two versions or a file vs vault")
    p.add_argument("--version-a", type=int, dest="version_a", default=None)
    p.add_argument("--version-b", type=int, dest="version_b", default=None)
    p.add_argument("--file", default=None, help="Local .env file to compare against vault")
    p.set_defaults(func=cmd_compare)
