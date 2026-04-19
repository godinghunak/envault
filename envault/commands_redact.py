"""CLI commands for redacting sensitive env values."""

import argparse
import sys
from envault.env_redact import redact_env
from envault.export import export_latest, export_version


def cmd_redact(args: argparse.Namespace) -> None:
    """Print a redacted view of an env version or file."""
    if hasattr(args, 'file') and args.file:
        try:
            with open(args.file, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: file '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
    else:
        version: int | None = getattr(args, 'version', None)
        try:
            if version is not None:
                content = export_version(args.vault_dir, version, args.password)
            else:
                content = export_latest(args.vault_dir, args.password)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    print(redact_env(content))


def register(subparsers) -> None:
    p = subparsers.add_parser("redact", help="Display env with sensitive values redacted")
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--password", required=False, default="", help="Vault password")
    p.add_argument("--version", type=int, default=None, help="Version to redact")
    p.add_argument("--file", default=None, help="Redact a local .env file instead")
    p.set_defaults(func=cmd_redact)
