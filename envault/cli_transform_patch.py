"""Register transform commands with the main CLI."""
from __future__ import annotations

import argparse

from envault.commands_transform import register as _register


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    _register(subparsers)
