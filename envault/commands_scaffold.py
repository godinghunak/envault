"""CLI commands for the scaffold feature."""
from __future__ import annotations

import sys
from pathlib import Path

from envault.env_scaffold import (
    ScaffoldError,
    scaffold_from_keys,
    scaffold_from_template,
    scaffold_to_file,
)


def cmd_scaffold(args) -> None:  # noqa: ANN001
    """Generate a scaffold .env file.

    Sub-modes:
      --keys KEY1 KEY2 ...   generate from explicit key names
      --template FILE        generate from a template file
    """
    dest = Path(args.output) if args.output else Path(".env.scaffold")
    overwrite = getattr(args, "overwrite", False)

    try:
        if args.template:
            template_path = Path(args.template)
            if not template_path.exists():
                print(f"[error] Template file not found: {template_path}", file=sys.stderr)
                sys.exit(1)
            content = scaffold_from_template(template_path.read_text(encoding="utf-8"))
        elif args.keys:
            content = scaffold_from_keys(args.keys, default_value=args.default or "")
        else:
            print("[error] Provide --keys or --template.", file=sys.stderr)
            sys.exit(1)

        out_path = scaffold_to_file(content, dest, overwrite=overwrite)
        print(f"Scaffold written to {out_path}")
    except ScaffoldError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)


def register(subparsers) -> None:  # noqa: ANN001
    p = subparsers.add_parser("scaffold", help="Generate a scaffold .env file")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--keys", nargs="+", metavar="KEY", help="Key names to scaffold")
    src.add_argument("--template", metavar="FILE", help="Template .env file to scaffold from")
    p.add_argument("--output", "-o", metavar="FILE", help="Destination file (default: .env.scaffold)")
    p.add_argument("--default", metavar="VALUE", default="", help="Default value for each key (default: empty)")
    p.add_argument("--overwrite", action="store_true", help="Overwrite destination if it exists")
    p.set_defaults(func=cmd_scaffold)
