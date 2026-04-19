"""Policy enforcement for vault: define rules that must pass before a push."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any


def _policy_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault" / "policy.json"


def load_policy(vault_dir: str) -> dict:
    p = _policy_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_policy(vault_dir: str, policy: dict) -> None:
    p = _policy_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(policy, indent=2))


def set_rule(vault_dir: str, name: str, value: Any) -> None:
    policy = load_policy(vault_dir)
    policy[name] = value
    save_policy(vault_dir, policy)


def remove_rule(vault_dir: str, name: str) -> None:
    policy = load_policy(vault_dir)
    if name not in policy:
        raise KeyError(f"Rule '{name}' not found")
    del policy[name]
    save_policy(vault_dir, policy)


class PolicyViolation(Exception):
    def __init__(self, violations: list[str]):
        self.violations = violations
        super().__init__("Policy violations: " + "; ".join(violations))


def enforce_policy(vault_dir: str, env_dict: dict[str, str]) -> list[str]:
    """Return list of violation messages; empty list means pass."""
    policy = load_policy(vault_dir)
    violations: list[str] = []

    if policy.get("require_keys"):
        for key in policy["require_keys"]:
            if key not in env_dict:
                violations.append(f"Required key missing: {key}")

    if policy.get("forbidden_keys"):
        for key in policy["forbidden_keys"]:
            if key in env_dict:
                violations.append(f"Forbidden key present: {key}")

    if policy.get("max_keys") is not None:
        if len(env_dict) > policy["max_keys"]:
            violations.append(f"Too many keys: {len(env_dict)} > {policy['max_keys']}")

    if policy.get("no_empty_values"):
        for k, v in env_dict.items():
            if v == "":
                violations.append(f"Empty value for key: {k}")

    return violations
