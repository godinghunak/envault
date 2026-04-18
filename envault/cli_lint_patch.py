"""Register lint subcommands on the CLI parser."""
from __future__ import annotations
from envault.commands_lint import cmd_lint


def register(subparsers, common_args) -> None:
    p = subparsers.add_parser("lint", help="Lint a .env file or vault version")
    common_args(p)
    group = p.add_mutually_exclusive_group()
    group.add_argument(
        "--version", "-n", type=int, default=None,
        help="Version number to lint (default: latest)"
    )
    group.add_argument(
        "--file", "-f", default=None,
        help="Path to a local .env file to lint"
    )
    p.set_defaults(func=cmd_lint)
