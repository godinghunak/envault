"""CLI commands for retention policy management."""
from __future__ import annotations

import sys

from envault.env_retention import (
    apply_retention,
    clear_policy,
    get_policy,
    set_policy,
)
from envault.vault import load_manifest


def cmd_retention_set(args) -> None:
    try:
        set_policy(args.vault_dir, args.max_versions, args.min_keep)
        print(
            f"Retention policy set: max_versions={args.max_versions}, "
            f"min_keep={args.min_keep}"
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_retention_show(args) -> None:
    policy = get_policy(args.vault_dir)
    if policy is None:
        print("No retention policy configured.")
    else:
        print(f"max_versions : {policy['max_versions']}")
        print(f"min_keep     : {policy['min_keep']}")


def cmd_retention_clear(args) -> None:
    clear_policy(args.vault_dir)
    print("Retention policy cleared.")


def cmd_retention_apply(args) -> None:
    manifest = load_manifest(args.vault_dir)
    versions = [int(v) for v in manifest.get("versions", {}).keys()]
    to_prune = apply_retention(args.vault_dir, versions)
    if not to_prune:
        print("Nothing to prune under current retention policy.")
        return
    print(f"Versions to prune ({len(to_prune)}): {', '.join(str(v) for v in to_prune)}")


def register(subparsers) -> None:
    p = subparsers.add_parser("retention", help="Manage version retention policy")
    sp = p.add_subparsers(dest="retention_cmd")

    p_set = sp.add_parser("set", help="Set retention policy")
    p_set.add_argument("max_versions", type=int, help="Maximum versions to keep")
    p_set.add_argument("--min-keep", type=int, default=1, dest="min_keep")
    p_set.set_defaults(func=cmd_retention_set)

    p_show = sp.add_parser("show", help="Show current retention policy")
    p_show.set_defaults(func=cmd_retention_show)

    p_clear = sp.add_parser("clear", help="Clear retention policy")
    p_clear.set_defaults(func=cmd_retention_clear)

    p_apply = sp.add_parser("apply", help="Preview versions that would be pruned")
    p_apply.set_defaults(func=cmd_retention_apply)
