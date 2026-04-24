"""CLI commands for managing deprecated keys."""

from __future__ import annotations

from envault.env_deprecate import (
    check_env_for_deprecated,
    deprecate_key,
    get_deprecation,
    list_deprecated,
    undeprecate_key,
)
from envault.export import export_latest


def _load_env(vault_dir: str, password: str) -> dict:
    from envault.diff import parse_env

    text = export_latest(vault_dir, password)
    return parse_env(text)


def cmd_deprecate_add(args) -> None:
    try:
        deprecate_key(
            args.vault_dir,
            args.key,
            reason=getattr(args, "reason", "") or "",
            replacement=getattr(args, "replacement", None),
        )
        print(f"Key '{args.key}' marked as deprecated.")
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_deprecate_remove(args) -> None:
    undeprecate_key(args.vault_dir, args.key)
    print(f"Key '{args.key}' removed from deprecations.")


def cmd_deprecate_list(args) -> None:
    keys = list_deprecated(args.vault_dir)
    if not keys:
        print("No deprecated keys.")
        return
    for key in keys:
        info = get_deprecation(args.vault_dir, key)
        replacement = info.get("replacement")
        reason = info.get("reason", "")
        suffix = f" -> {replacement}" if replacement else ""
        note = f"  ({reason})" if reason else ""
        print(f"  {key}{suffix}{note}")


def cmd_deprecate_check(args) -> None:
    try:
        env = _load_env(args.vault_dir, args.password)
    except Exception as exc:
        print(f"Error loading vault: {exc}")
        return
    issues = check_env_for_deprecated(args.vault_dir, env)
    if not issues:
        print("No deprecated keys found in latest version.")
        return
    print(f"{len(issues)} deprecated key(s) found:")
    for issue in issues:
        replacement = issue["replacement"]
        reason = issue["reason"]
        suffix = f" -> {replacement}" if replacement else ""
        note = f"  ({reason})" if reason else ""
        print(f"  {issue['key']}{suffix}{note}")


def register(subparsers) -> None:
    p = subparsers.add_parser("deprecate", help="Manage deprecated env keys")
    sp = p.add_subparsers(dest="deprecate_cmd", required=True)

    add_p = sp.add_parser("add", help="Mark a key as deprecated")
    add_p.add_argument("key")
    add_p.add_argument("--reason", default="", help="Reason for deprecation")
    add_p.add_argument("--replacement", default=None, help="Suggested replacement key")
    add_p.set_defaults(func=cmd_deprecate_add)

    rm_p = sp.add_parser("remove", help="Remove a deprecation marker")
    rm_p.add_argument("key")
    rm_p.set_defaults(func=cmd_deprecate_remove)

    ls_p = sp.add_parser("list", help="List deprecated keys")
    ls_p.set_defaults(func=cmd_deprecate_list)

    chk_p = sp.add_parser("check", help="Check latest version for deprecated keys")
    chk_p.add_argument("--password", required=True)
    chk_p.set_defaults(func=cmd_deprecate_check)
