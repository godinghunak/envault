"""Patch CLI parser to add export subcommands."""
from envault.commands_export import cmd_export


def register(subparsers):
    p = subparsers.add_parser("export", help="Export a decrypted .env version")
    p.add_argument("vault_dir", help="Path to the project vault directory")
    p.add_argument("password", help="Encryption password")
    p.add_argument(
        "--version", type=int, default=None,
        help="Version number to export (default: latest)"
    )
    p.add_argument(
        "--output", "-o", default=None,
        help="Output file path (default: stdout)"
    )
    p.set_defaults(func=cmd_export)
