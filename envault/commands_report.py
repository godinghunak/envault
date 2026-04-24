"""CLI command for generating a vault report."""

from __future__ import annotations

import argparse

from envault.vault import init_vault
from envault.env_report import build_report


def cmd_report(args: argparse.Namespace) -> None:
    """Print a full status report for the vault."""
    vault_dir = getattr(args, "vault_dir", ".envault")
    password = args.password
    limit = getattr(args, "limit", 5)

    init_vault(vault_dir)

    try:
        report = build_report(vault_dir, password, limit=limit)
        print(report.render())
    except Exception as exc:  # pragma: no cover
        print(f"Error generating report: {exc}")
        raise SystemExit(1)


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("report", help="Generate a vault status report")
    p.add_argument("--password", required=True, help="Vault password")
    p.add_argument(
        "--limit",
        type=int,
        default=5,
        metavar="N",
        help="Number of recent audit events to show (default: 5)",
    )
    p.add_argument(
        "--vault-dir",
        default=".envault",
        metavar="DIR",
        help="Path to the vault directory",
    )
    p.set_defaults(func=cmd_report)
