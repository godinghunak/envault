"""CLI commands for env key reordering."""
import argparse
from envault.vault import init_vault
from envault.env_reorder import reorder_version, reorder_latest


def cmd_reorder(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    init_vault(vault_dir)
    password = args.password
    alphabetical = getattr(args, "alphabetical", False)
    key_order: list[str] = args.keys if args.keys else []

    if not key_order and not alphabetical:
        print("Error: provide --keys or --alphabetical.")
        return

    if args.version is not None:
        new_v = reorder_version(vault_dir, args.version, password, key_order, alphabetical)
    else:
        new_v = reorder_latest(vault_dir, password, key_order, alphabetical)

    print(f"Reordered keys → version {new_v}")


def register(subparsers) -> None:
    p = subparsers.add_parser("reorder", help="Reorder keys in an env version")
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--password", required=True, help="Vault password")
    p.add_argument("--version", type=int, default=None, help="Version to reorder (default: latest)")
    p.add_argument("--keys", nargs="*", default=[], metavar="KEY",
                   help="Ordered list of keys to place first")
    p.add_argument("--alphabetical", action="store_true",
                   help="Sort all keys alphabetically")
    p.set_defaults(func=cmd_reorder)
