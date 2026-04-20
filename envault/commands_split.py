"""CLI commands for env-split feature."""

import argparse
from envault.env_split import split_by_prefix, split_env_text, split_by_keys, format_split_part
from envault.vault import load_manifest
from envault.export import export_latest, export_version


def cmd_split(args: argparse.Namespace) -> None:
    """Split the latest (or specified) vault version by prefix and print each group."""
    vault_dir = args.vault_dir

    if hasattr(args, "version") and args.version:
        text = export_version(vault_dir, args.version, args.password)
    else:
        text = export_latest(vault_dir, args.password)

    sep = getattr(args, "sep", "_") or "_"
    result = split_env_text(text, sep=sep)

    if not result.names():
        print("No keys found.")
        return

    for name in result.names():
        part = result.get(name)
        print(f"[{name}]")
        for k, v in sorted(part.items()):
            print(f"  {k}={v}")
        print()


def register(subparsers) -> None:
    p = subparsers.add_parser("split", help="Split vault env into prefix-based groups")
    p.add_argument("--password", required=True, help="Vault password")
    p.add_argument("--version", type=int, default=None, help="Version to split (default: latest)")
    p.add_argument("--sep", default="_", help="Key separator for prefix splitting (default: _)")
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.set_defaults(func=cmd_split)
