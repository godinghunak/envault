"""Register diff subcommand onto the envault CLI parser."""
from __future__ import annotations
import argparse
from envault.commands_diff import cmd_diff


def register(subparsers: argparse._SubParsersAction, common: argparse.ArgumentParser) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("diff", parents=[common], help="Diff two env versions")
    p.add_argument(
        "--v1",
        type=int,
        default=None,
        metavar="VERSION",
        help="Older version number (default: second-to-last)",
    )
    p.add_argument(
        "--v2",
        type=int,
        default=None,
        metavar="VERSION",
        help="Newer version number (default: last)",
    )
    p.add_argument(
        "--show-values",
        action="store_true",
        default=False,
        help="Show actual values in diff output",
    )
    p.set_defaults(func=cmd_diff)
