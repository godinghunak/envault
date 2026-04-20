"""CLI commands for env-schema validation."""

from __future__ import annotations

import argparse
import sys

from envault.env_validate import validate_version, validate_file


def cmd_validate(args: argparse.Namespace) -> None:
    """Validate a vault version or a plain file against a schema."""
    schema = args.schema

    if args.file:
        report = validate_file(args.file, schema)
        source = f"file '{args.file}'"
    else:
        version = getattr(args, "version", None)
        vault_dir = args.vault_dir
        password = args.password
        report = validate_version(vault_dir, password, schema, version)
        source = f"version {report.version}"

    if report.ok:
        print(f"[OK] {source} passes schema '{schema}'")
    else:
        print(f"[FAIL] {source} has {len(report.violations)} violation(s):")
        for v in report.violations:
            print(f"  - {v}")
        sys.exit(1)


def register(subparsers) -> None:  # noqa: ANN001
    p = subparsers.add_parser(
        "validate",
        help="Validate a .env version or file against a schema",
    )
    p.add_argument("schema", help="Path to schema file (.envschema)")
    p.add_argument(
        "--file",
        default=None,
        metavar="FILE",
        help="Validate a plain .env file instead of a vault version",
    )
    p.add_argument(
        "--version",
        type=int,
        default=None,
        metavar="N",
        help="Vault version to validate (default: latest)",
    )
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--password", default="", help="Vault password")
    p.set_defaults(func=cmd_validate)
