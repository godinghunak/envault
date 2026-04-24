"""commands_diff_summary.py — CLI command for the diff-summary feature."""
from __future__ import annotations

import argparse
import sys

from envault.env_diff_summary import summarize_diff, format_diff_summary
from envault.vault import load_manifest


def cmd_diff_summary(args: argparse.Namespace) -> None:
    """Print a concise summary of changes between two vault versions."""
    vault_dir: str = args.vault_dir
    password: str = args.password

    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])

    if len(versions) < 2:
        print("At least two versions are required for a diff summary.")
        sys.exit(1)

    version_a: str = args.version_a if args.version_a else str(len(versions) - 1)
    version_b: str = args.version_b if args.version_b else str(len(versions))

    try:
        summary = summarize_diff(vault_dir, version_a, version_b, password)
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}")
        sys.exit(1)

    print(format_diff_summary(summary))

    if args.exit_code and summary.has_changes:
        sys.exit(2)


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "diff-summary",
        help="Show a concise summary of changes between two versions",
    )
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--password", required=True, help="Vault password")
    p.add_argument("version_a", nargs="?", default=None, help="First version (default: second-latest)")
    p.add_argument("version_b", nargs="?", default=None, help="Second version (default: latest)")
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 2 if differences are found",
    )
    p.set_defaults(func=cmd_diff_summary)
