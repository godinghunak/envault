"""Import .env content from external sources into the vault."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional

from envault.vault import init_vault, add_version
from envault.lint import lint_env


def import_from_file(vault_dir: str, filepath: str, password: str, strict: bool = False) -> int:
    """Import a .env file into the vault. Returns new version number."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    content = path.read_text()
    if strict:
        issues = lint_env(content)
        if issues:
            msgs = "\n".join(str(i) for i in issues)
            raise ValueError(f"Lint errors in {filepath}:\n{msgs}")
    init_vault(vault_dir)
    version = add_version(vault_dir, content, password)
    return version


def import_from_string(vault_dir: str, content: str, password: str, strict: bool = False) -> int:
    """Import raw env content string into the vault. Returns new version number."""
    if strict:
        issues = lint_env(content)
        if issues:
            msgs = "\n".join(str(i) for i in issues)
            raise ValueError(f"Lint errors in content:\n{msgs}")
    init_vault(vault_dir)
    version = add_version(vault_dir, content, password)
    return version


def import_from_env(vault_dir: str, keys: Optional[list], password: str) -> int:
    """Import selected (or all) keys from current process environment."""
    if keys:
        pairs = {k: os.environ[k] for k in keys if k in os.environ}
    else:
        pairs = dict(os.environ)
    content = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    init_vault(vault_dir)
    version = add_version(vault_dir, content, password)
    return version
