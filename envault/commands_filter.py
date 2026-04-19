"""CLI commands for env-filter feature."""
from __future__ import annotations
import argparse
from envault.env_filter import filter_version, format_filtered


def cmd_filter(args: argparse.Namespace) -> None:
    pattern = getattr(args, "pattern", "*") or "*"
    prefix = getattr(args, "prefix", None)
    version = getattr(args, "version", None)

    result = filter_version(
        vault_dir=args.vault_dir,
        password=args.password,
        pattern=pattern,
        version=version,
        prefix=prefix,
    )

    if not result:
        print("No keys matched.")
        return

    output = format_filtered(result)
    if getattr(args, "output", None):
        with open(args.output, "w") as f:
            f.write(output + "\n")
        print(f"Wrote {len(result)} key(s) to {args.output}")
    else:
        print(output)


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("filter", help="Filter keys from a vault version")
    p.add_argument("--pattern", default="*", help="Glob pattern for key names")
    p.add_argument("--prefix", default=None, help="Key prefix filter")
    p.add_argument("--version", type=int, default=None, help="Version number (default: latest)")
    p.add_argument("--output", default=None, help="Write result to file")
    p.set_defaults(func=cmd_filter)
