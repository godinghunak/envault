"""CLI commands for pruning old vault versions."""

import argparse
from envault.vault import init_vault
from envault.env_prune import prune_versions, prune_preview


def cmd_prune(args: argparse.Namespace) -> None:
    init_vault(args.vault_dir)

    keep = args.keep

    if args.dry_run:
        preview = prune_preview(args.vault_dir, keep=keep)
        if not preview["to_prune"]:
            print(f"Nothing to prune (fewer than {keep} versions stored).")
        else:
            print(f"Would prune versions: {preview['to_prune']}")
            print(f"Would keep versions:  {preview['to_keep']}")
        return

    pruned = prune_versions(args.vault_dir, password=args.password, keep=keep)
    if not pruned:
        print(f"Nothing to prune (fewer than {keep} versions stored).")
    else:
        print(f"Pruned {len(pruned)} version(s): {pruned}")


def register(subparsers) -> None:
    p = subparsers.add_parser("prune", help="Remove old encrypted versions from the vault")
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--password", default="", help="Vault password")
    p.add_argument(
        "--keep",
        type=int,
        default=5,
        metavar="N",
        help="Number of most-recent versions to keep (default: 5)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be pruned without deleting",
    )
    p.set_defaults(func=cmd_prune)
