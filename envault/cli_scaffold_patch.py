"""Register scaffold commands with the main CLI parser."""
from __future__ import annotations

from envault.commands_scaffold import register


def register_scaffold(subparsers) -> None:  # noqa: ANN001
    register(subparsers)
