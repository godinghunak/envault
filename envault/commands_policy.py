"""CLI commands for vault policy management."""
from __future__ import annotations
import json
from envault.env_policy import (
    load_policy, set_rule, remove_rule, enforce_policy, PolicyViolation
)
from envault.diff import parse_env
from envault.export import export_latest


def cmd_policy_set(args) -> None:
    vault_dir = args.vault_dir
    name = args.name
    try:
        value = json.loads(args.value)
    except json.JSONDecodeError:
        value = args.value
    set_rule(vault_dir, name, value)
    print(f"Policy rule '{name}' set to {value!r}")


def cmd_policy_remove(args) -> None:
    vault_dir = args.vault_dir
    try:
        remove_rule(vault_dir, args.name)
        print(f"Policy rule '{args.name}' removed")
    except KeyError as e:
        print(str(e))


def cmd_policy_show(args) -> None:
    vault_dir = args.vault_dir
    policy = load_policy(vault_dir)
    if not policy:
        print("No policy rules defined.")
        return
    for k, v in policy.items():
        print(f"  {k}: {json.dumps(v)}")


def cmd_policy_check(args) -> None:
    vault_dir = args.vault_dir
    password = args.password
    try:
        content = export_latest(vault_dir, password)
    except Exception as e:
        print(f"Error reading vault: {e}")
        return
    env_dict = parse_env(content)
    violations = enforce_policy(vault_dir, env_dict)
    if not violations:
        print("Policy check passed.")
    else:
        print("Policy violations found:")
        for v in violations:
            print(f"  - {v}")


def register(subparsers, parent_parser) -> None:
    p = subparsers.add_parser("policy", help="Manage vault push policies")
    sp = p.add_subparsers(dest="policy_cmd")

    ps = sp.add_parser("set", help="Set a policy rule")
    ps.add_argument("name")
    ps.add_argument("value")
    ps.set_defaults(func=cmd_policy_set)

    pr = sp.add_parser("remove", help="Remove a policy rule")
    pr.add_argument("name")
    pr.set_defaults(func=cmd_policy_remove)

    psh = sp.add_parser("show", help="Show current policy")
    psh.set_defaults(func=cmd_policy_show)

    pch = sp.add_parser("check", help="Check latest vault version against policy")
    pch.add_argument("--password", required=True)
    pch.set_defaults(func=cmd_policy_check)
