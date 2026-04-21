"""CLI command for type-checking vault versions against a type schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.env_typecheck import KNOWN_TYPES, typecheck_env
from envault.export import export_latest, export_version
from envault.vault import load_manifest


def _parse_schema_file(path: str) -> dict:
    """Parse a simple KEY=type schema file."""
    schema: dict = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, type_name = line.partition("=")
        key = key.strip()
        type_name = type_name.strip()
        if type_name not in KNOWN_TYPES:
            print(f"[warn] Unknown type '{type_name}' for key '{key}' — skipping.")
            continue
        schema[key] = type_name
    return schema


def cmd_typecheck(args: argparse.Namespace) -> None:
    schema = _parse_schema_file(args.schema)
    if not schema:
        print("No valid type rules found in schema file.")
        sys.exit(1)

    if args.version is not None:
        manifest = load_manifest(args.vault_dir)
        versions = manifest.get("versions", [])
        if args.version < 1 or args.version > len(versions):
            print(f"Version {args.version} does not exist.")
            sys.exit(1)
        env_text = export_version(args.vault_dir, args.version, args.password)
        label = f"v{args.version}"
    else:
        env_text = export_latest(args.vault_dir, args.password)
        label = "latest"

    violations = typecheck_env(env_text, schema)

    if not violations:
        print(f"[ok] No type violations found in {label}.")
    else:
        print(f"[fail] {len(violations)} type violation(s) in {label}:")
        for v in violations:
            print(f"  {v}")
        sys.exit(1)


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "typecheck",
        help="Check env values against a type schema file",
    )
    p.add_argument("schema", help="Path to type schema file (KEY=type per line)")
    p.add_argument(
        "--version", type=int, default=None, help="Version to check (default: latest)"
    )
    p.add_argument("--password", required=True, help="Vault password")
    p.add_argument("--vault-dir", default=".envault", dest="vault_dir")
    p.set_defaults(func=cmd_typecheck)
