"""CLI commands for env-transform feature."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envault.env_transform import apply_transforms, list_transforms
from envault.export import export_latest, export_version
from envault.vault import load_manifest


def _load_env_dict(vault_dir: str, version: int | None) -> dict:
    from envault.diff import parse_env

    if version is None:
        text = export_latest(vault_dir)
    else:
        text = export_version(vault_dir, version)
    return parse_env(text)


def cmd_transform(args: argparse.Namespace) -> None:
    transforms: List[str] = args.transforms

    if not transforms:
        print("Error: at least one transform name is required.", file=sys.stderr)
        sys.exit(1)

    try:
        env = _load_env_dict(args.vault_dir, getattr(args, "version", None))
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        result = apply_transforms(env, transforms)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    for k, v in result.transformed.items():
        print(f"{k}={v}")

    if args.verbose:
        print(f"\n# Applied: {', '.join(result.applied)}", file=sys.stderr)
        print(f"# Changed keys: {result.changed_keys}", file=sys.stderr)


def cmd_transform_list(args: argparse.Namespace) -> None:
    rules = list_transforms()
    if not rules:
        print("No transforms available.")
        return
    for rule in rules:
        print(f"  {rule.name:<20} {rule.description}")


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("transform", help="Apply transformations to env keys/values")
    sub = p.add_subparsers(dest="transform_cmd")

    run_p = sub.add_parser("run", help="Apply transforms and print result")
    run_p.add_argument("transforms", nargs="+", help="Transform names to apply in order")
    run_p.add_argument("--version", type=int, default=None, help="Version to transform (default: latest)")
    run_p.add_argument("--verbose", action="store_true", help="Print summary to stderr")
    run_p.set_defaults(func=cmd_transform)

    list_p = sub.add_parser("list", help="List available transforms")
    list_p.set_defaults(func=cmd_transform_list)
