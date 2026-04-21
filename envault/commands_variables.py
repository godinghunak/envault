"""CLI commands for variable substitution inspection and resolution."""

from __future__ import annotations

import argparse

from envault.vault import load_manifest
from envault.export import export_version, export_latest
from envault.diff import parse_env
from envault.env_variables import (
    resolve_env,
    find_unresolved,
    find_references,
    SubstitutionError,
)


def _load_env(vault_dir: str, version: int | None) -> dict[str, str]:
    if version is None:
        content = export_latest(vault_dir, password="")
    else:
        content = export_version(vault_dir, version, password="")
    return parse_env(content)


def cmd_vars_resolve(args: argparse.Namespace) -> None:
    """Print the env with all ${VAR} references expanded."""
    env = _load_env(args.vault_dir, getattr(args, "version", None))
    try:
        resolved = resolve_env(env, strict=not args.lenient)
    except SubstitutionError as exc:
        print(f"Error: {exc}")
        return
    for k, v in resolved.items():
        print(f"{k}={v}")


def cmd_vars_check(args: argparse.Namespace) -> None:
    """List keys with unresolvable ${VAR} references."""
    env = _load_env(args.vault_dir, getattr(args, "version", None))
    bad = find_unresolved(env)
    if not bad:
        print("All variable references are resolvable.")
    else:
        print(f"Found {len(bad)} key(s) with unresolvable references:")
        for k in bad:
            refs = find_references(env[k])
            print(f"  {k}: references {refs}")


def cmd_vars_list(args: argparse.Namespace) -> None:
    """List all ${VAR} references found in the env."""
    env = _load_env(args.vault_dir, getattr(args, "version", None))
    any_found = False
    for k, v in env.items():
        refs = find_references(v)
        if refs:
            any_found = True
            print(f"  {k} -> {refs}")
    if not any_found:
        print("No variable references found.")


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("vars", help="Variable substitution tools")
    sp = p.add_subparsers(dest="vars_cmd", required=True)

    for name, fn, help_text in [
        ("resolve", cmd_vars_resolve, "Expand ${VAR} references and print result"),
        ("check", cmd_vars_check, "Report unresolvable references"),
        ("list", cmd_vars_list, "List all references found in env"),
    ]:
        sub = sp.add_parser(name, help=help_text)
        sub.add_argument("--vault-dir", default=".envault")
        sub.add_argument("--version", type=int, default=None)
        if name == "resolve":
            sub.add_argument(
                "--lenient", action="store_true",
                help="Leave unresolvable refs as-is instead of erroring"
            )
        sub.set_defaults(func=fn)
