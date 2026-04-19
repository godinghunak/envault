"""CLI commands for masking sensitive env values."""

import argparse
import sys

from envault.vault import load_manifest
from envault.export import export_version, export_latest
from envault.env_mask import mask_env_text, mask_dict
from envault.diff import parse_env


def cmd_mask(args: argparse.Namespace) -> None:
    """Print env version with sensitive values masked."""
    vault_dir = args.vault_dir
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])

    if not versions:
        print("No versions found.", file=sys.stderr)
        sys.exit(1)

    version = getattr(args, "version", None)
    if version is None:
        plaintext = export_latest(vault_dir, args.password)
    else:
        if version not in versions:
            print(f"Version '{version}' not found.", file=sys.stderr)
            sys.exit(1)
        plaintext = export_version(vault_dir, version, args.password)

    show_chars = getattr(args, "show_chars", 0)
    masked = mask_env_text(plaintext, show_chars=show_chars)
    print(masked)


def register(subparsers) -> None:
    p = subparsers.add_parser("mask", help="Print env with sensitive values masked")
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--password", required=True, help="Vault password")
    p.add_argument("--version", default=None, help="Version to mask (default: latest)")
    p.add_argument(
        "--show-chars",
        type=int,
        default=0,
        dest="show_chars",
        help="Reveal last N characters of masked values",
    )
    p.set_defaults(func=cmd_mask)
