"""cli_supersede_patch.py – register supersede commands with the main CLI."""
from __future__ import annotations

from envault.commands_supersede import register


def register_supersede(subparsers, vault_dir: str) -> None:  # noqa: ANN001
    register(subparsers, vault_dir)
