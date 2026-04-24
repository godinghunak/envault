"""CLI commands for required-key checking."""

from __future__ import annotations

import argparse
from pathlib import Path

from envault.env_required import (
    check_required_from_text,
    format_result,
    load_required_keys,
)
from envault.export import export_latest, export_version
from envault.vault import load_manifest


def _latest_version(vault_dir: str) -> int:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions found in vault.")
    return max(int(v) for v in versions)


def cmd_required_check(args: argparse.Namespace) -> None:
    required_path = Path(args.required_file)
    if not required_path.exists():
        print(f"Required-keys file not found: {required_path}")
        return

    required_text = required_path.read_text()

    if args.file:
        env_text = Path(args.file).read_text()
    elif args.version:
        env_text = export_version(args.vault_dir, int(args.version), args.password)
    else:
        env_text = export_latest(args.vault_dir, args.password)

    result = check_required_from_text(env_text, required_text)
    print(format_result(result))
    if not result.ok:
        raise SystemExit(1)


def cmd_required_list(args: argparse.Namespace) -> None:
    required_path = Path(args.required_file)
    if not required_path.exists():
        print(f"Required-keys file not found: {required_path}")
        return
    keys = load_required_keys(required_path.read_text())
    if not keys:
        print("No required keys defined.")
    else:
        for key in sorted(keys):
            print(f"  {key}")


def register(subparsers: argparse._SubParsersAction, parent: argparse.ArgumentParser) -> None:  # noqa: SLF001
    p = subparsers.add_parser("required", help="Check required keys", parents=[parent])
    sp = p.add_subparsers(dest="required_cmd", required=True)

    chk = sp.add_parser("check", help="Check env against required keys", parents=[parent])
    chk.add_argument("required_file", help="Path to required-keys file")
    chk.add_argument("--file", default=None, help="Check a local .env file instead of vault")
    chk.add_argument("--version", default=None, help="Vault version to check")
    chk.set_defaults(func=cmd_required_check)

    lst = sp.add_parser("list", help="List required keys", parents=[parent])
    lst.add_argument("required_file", help="Path to required-keys file")
    lst.set_defaults(func=cmd_required_list)
