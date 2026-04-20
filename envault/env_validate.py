"""Validate a .env file or vault version against a schema file."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from envault.env_schema import load_text, validate_env
from envault.export import export_version, export_latest
from envault.vault import load_manifest


class ValidationReport:
    def __init__(self, version: int, violations: list):
        self.version = version
        self.violations = violations

    @property
    def ok(self) -> bool:
        return len(self.violations) == 0

    def __repr__(self) -> str:  # pragma: no cover
        return f"ValidationReport(version={self.version}, ok={self.ok}, issues={len(self.violations)})"


def validate_version(
    vault_dir: str,
    password: str,
    schema_path: str,
    version: Optional[int] = None,
) -> ValidationReport:
    """Decrypt a vault version and validate it against *schema_path*."""
    schema_text = Path(schema_path).read_text()
    schema = load_text(schema_text)

    if version is None:
        manifest = load_manifest(vault_dir)
        versions = manifest.get("versions", [])
        if not versions:
            raise ValueError("No versions in vault")
        version = versions[-1]["version"]
        plaintext = export_latest(vault_dir, password)
    else:
        plaintext = export_version(vault_dir, password, version)

    env_dict = {}
    for line in plaintext.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            env_dict[k.strip()] = v.strip()

    violations = validate_env(env_dict, schema)
    return ValidationReport(version=version, violations=violations)


def validate_file(
    file_path: str,
    schema_path: str,
) -> ValidationReport:
    """Validate a plain .env file against *schema_path* (no decryption)."""
    schema_text = Path(schema_path).read_text()
    schema = load_text(schema_text)

    env_dict = {}
    for line in Path(file_path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            env_dict[k.strip()] = v.strip()

    violations = validate_env(env_dict, schema)
    return ValidationReport(version=0, violations=violations)
