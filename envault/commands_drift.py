"""CLI command for drift detection between a live .env file and a vault version."""
from __future__ import annotations

import sys
from pathlib import Path

from envault.export import export_version, export_latest
from envault.env_drift import detect_drift_from_text, format_drift


def cmd_drift(args) -> None:
    """Compare a local .env file against a stored vault version."""
    vault_dir = args.vault_dir
    env_path = Path(args.file)

    if not env_path.exists():
        print(f"Error: file not found: {env_path}", file=sys.stderr)
        sys.exit(1)

    try:
        if hasattr(args, "version") and args.version:
            vault_text = export_version(vault_dir, args.version, args.password)
        else:
            vault_text = export_latest(vault_dir, args.password)
    except Exception as exc:  # noqa: BLE001
        print(f"Error reading vault: {exc}", file=sys.stderr)
        sys.exit(1)

    file_text = env_path.read_text(encoding="utf-8")
    result = detect_drift_from_text(vault_text, file_text)
    print(format_drift(result))

    if result.has_drift and getattr(args, "fail_on_drift", False):
        sys.exit(1)


def register(subparsers) -> None:
    p = subparsers.add_parser("drift", help="Detect drift between a .env file and the vault")
    p.add_argument("file", help="Path to the local .env file")
    p.add_argument("--version", "-v", type=int, default=None, help="Vault version to compare (default: latest)")
    p.add_argument("--password", "-p", required=True, help="Vault password")
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--fail-on-drift", action="store_true", help="Exit with code 1 if drift is found")
    p.set_defaults(func=cmd_drift)
