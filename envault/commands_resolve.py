"""CLI commands for resolving env variable references."""
from __future__ import annotations

import sys
from typing import Optional

from envault.vault import load_manifest
from envault.export import export_version, export_latest
from envault.env_resolve import resolve_references, format_resolve_result
from envault.diff import parse_env


def _load_env(vault_dir: str, version: Optional[int]) -> dict:
    if version is not None:
        text = export_version(vault_dir, version)
    else:
        text = export_latest(vault_dir)
    return parse_env(text)


def cmd_resolve(args) -> None:
    """Resolve ${VAR} references within a vault version."""
    vault_dir = args.vault_dir
    version: Optional[int] = getattr(args, "version", None)
    strict: bool = getattr(args, "strict", False)
    overlay: Optional[str] = getattr(args, "overlay", None)

    try:
        base = _load_env(vault_dir, version)
    except Exception as exc:
        print(f"Error loading version: {exc}", file=sys.stderr)
        sys.exit(1)

    overrides: dict = {}
    if overlay is not None:
        try:
            ov_version = int(overlay)
            overrides = _load_env(vault_dir, ov_version)
        except ValueError:
            print(f"Invalid overlay version: {overlay}", file=sys.stderr)
            sys.exit(1)
        except Exception as exc:
            print(f"Error loading overlay: {exc}", file=sys.stderr)
            sys.exit(1)

    result = resolve_references(base, overrides, strict=strict)
    print(format_resolve_result(result))
    if not result.ok:
        sys.exit(2)


def register(subparsers) -> None:
    p = subparsers.add_parser("resolve", help="Resolve ${VAR} references in an env version")
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--version", type=int, default=None, help="Version to resolve (default: latest)")
    p.add_argument("--overlay", default=None, help="Version number to overlay on top of base")
    p.add_argument("--strict", action="store_true", help="Exit with error on unresolved references")
    p.set_defaults(func=cmd_resolve)
