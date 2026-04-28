"""CLI commands for regex-based env key/value operations."""
from __future__ import annotations
import sys
from envault.vault import load_manifest
from envault.export import export_latest, export_version
from envault.diff import parse_env
from envault.env_regex import (
    match_keys,
    match_values,
    validate_values,
    format_regex_result,
)


def _load_env(vault_dir: str, version: int | None):
    if version is None:
        raw = export_latest(vault_dir, password="")
    else:
        raw = export_version(vault_dir, version, password="")
    return parse_env(raw)


def _load_env_safe(vault_dir: str, args):
    """Load env dict; exit with error on failure."""
    try:
        version = getattr(args, "version", None)
        return _load_env(vault_dir, version)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading vault: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_regex_keys(args) -> None:
    """Search keys by regex pattern."""
    env = _load_env_safe(args.vault_dir, args)
    result = match_keys(env, args.pattern)
    print(format_regex_result(result))
    if not result.ok:
        sys.exit(1)


def cmd_regex_values(args) -> None:
    """Search values by regex pattern."""
    env = _load_env_safe(args.vault_dir, args)
    result = match_values(env, args.pattern)
    print(format_regex_result(result))
    if not result.ok:
        sys.exit(1)


def cmd_regex_validate(args) -> None:
    """Validate values against key=pattern rules passed as KEY=PATTERN args."""
    rules: dict[str, str] = {}
    for item in args.rules:
        if "=" not in item:
            print(f"Invalid rule (expected KEY=PATTERN): {item!r}", file=sys.stderr)
            sys.exit(1)
        k, _, p = item.partition("=")
        rules[k.strip()] = p.strip()
    env = _load_env_safe(args.vault_dir, args)
    result = validate_values(env, rules)
    print(format_regex_result(result))
    if not result.ok:
        sys.exit(1)


def register(subparsers) -> None:
    p_regex = subparsers.add_parser("regex", help="Regex-based env operations")
    rx_sub = p_regex.add_subparsers(dest="regex_cmd")

    pk = rx_sub.add_parser("keys", help="Match keys by regex")
    pk.add_argument("pattern", help="Regex pattern")
    pk.add_argument("--version", type=int, default=None)
    pk.add_argument("vault_dir")
    pk.set_defaults(func=cmd_regex_keys)

    pv = rx_sub.add_parser("values", help="Match values by regex")
    pv.add_argument("pattern", help="Regex pattern")
    pv.add_argument("--version", type=int, default=None)
    pv.add_argument("vault_dir")
    pv.set_defaults(func=cmd_regex_values)

    pval = rx_sub.add_parser("validate", help="Validate values against regex rules")
    pval.add_argument("rules", nargs="+", metavar="KEY=PATTERN")
    pval.add_argument("--version", type=int, default=None)
    pval.add_argument("vault_dir")
    pval.set_defaults(func=cmd_regex_validate)
