"""CLI commands for vault changelog."""

import argparse
from envault.env_changelog import build_changelog, format_changelog


def cmd_changelog(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    password = args.password
    from_version = getattr(args, "from_version", None)
    to_version = getattr(args, "to_version", None)

    try:
        entries = build_changelog(
            vault_dir,
            password,
            from_version=from_version,
            to_version=to_version,
        )
    except Exception as e:
        print(f"Error building changelog: {e}")
        return

    if not entries:
        print("No changelog entries found.")
        return

    print(format_changelog(entries))


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("changelog", help="Show changelog between versions")
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--password", required=True, help="Vault password")
    p.add_argument(
        "--from",
        dest="from_version",
        type=int,
        default=None,
        help="Start version (inclusive)",
    )
    p.add_argument(
        "--to",
        dest="to_version",
        type=int,
        default=None,
        help="End version (inclusive)",
    )
    p.set_defaults(func=cmd_changelog)
