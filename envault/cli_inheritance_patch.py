"""Register the inheritance sub-command with the main CLI parser."""
from __future__ import annotations


def register(subparsers) -> None:  # type: ignore[type-arg]
    from envault.commands_inheritance import register as _reg
    _reg(subparsers)
