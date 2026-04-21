"""Patch envault CLI to include the 'vars' subcommand group."""

from __future__ import annotations

import argparse
from envault.commands_variables import register as _register


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'vars' command group with the top-level parser."""
    _register(subparsers)
