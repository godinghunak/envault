"""CLI command for env blame."""
from __future__ import annotations
import argparse
import getpass

from envault.env_blame import blame


def cmd_blame(args: argparse.Namespace) -> None:
    password = getpass.getpass("Vault password: ")
    version = getattr(args, "version", None)
    try:
        lines = blame(args.vault_dir, password, version)
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    if not lines:
        print("No keys found.")
        return
    for line in lines:
        print(line)


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("blame", help="Show which version introduced each key")
    p.add_argument(
        "--version", type=int, default=None, metavar="N",
        help="Target version (default: latest)"
    )
    p.add_argument(
        "--vault-dir", default=".envault", metavar="DIR",
        help="Path to vault directory"
    )
    p.set_defaults(func=cmd_blame)
