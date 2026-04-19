"""Filter keys from a vault version by pattern or prefix."""
from __future__ import annotations
import fnmatch
from typing import Optional
from envault.vault import load_manifest
from envault.export import export_version, export_latest
from envault.diff import parse_env


def filter_env(env: dict[str, str], pattern: str) -> dict[str, str]:
    """Return keys matching a glob pattern."""
    return {k: v for k, v in env.items() if fnmatch.fnmatch(k, pattern)}


def filter_by_prefix(env: dict[str, str], prefix: str) -> dict[str, str]:
    """Return keys starting with prefix."""
    return {k: v for k, v in env.items() if k.startswith(prefix)}


def filter_version(
    vault_dir: str,
    password: str,
    pattern: str,
    version: Optional[int] = None,
    prefix: Optional[str] = None,
) -> dict[str, str]:
    """Decrypt a version and return filtered keys."""
    if version is None:
        content = export_latest(vault_dir, password)
    else:
        content = export_version(vault_dir, version, password)
    env = parse_env(content)
    if prefix is not None:
        env = filter_by_prefix(env, prefix)
    if pattern != "*":
        env = filter_env(env, pattern)
    return env


def format_filtered(env: dict[str, str]) -> str:
    """Format filtered env dict as .env lines."""
    return "\n".join(f"{k}={v}" for k, v in sorted(env.items()))
