"""CLI command for vault summary."""
from __future__ import annotations
import argparse

from envault.vault import init_vault
from envault.env_summary import summarize, format_summary


def cmd_summary(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    password = args.password
    init_vault(vault_dir)
    summary = summarize(vault_dir, password)
    print(format_summary(summary))


def register(subparsers, common_args=None) -> None:
    p = subparsers.add_parser("summary", help="Show a summary of the vault contents")
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--password", required=True, help="Vault password")
    if common_args:
        common_args(p)
    p.set_defaults(func=cmd_summary)
