"""Register the 'report' sub-command with the main CLI parser."""

from __future__ import annotations

import argparse

from envault.commands_report import register as _register


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    _register(subparsers)
