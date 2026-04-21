"""Patch envault CLI to include namespace subcommands."""
from __future__ import annotations

import argparse
from envault.commands_namespace import register as _register


def register(subparsers: argparse.Action, parent: argparse.ArgumentParser) -> None:
    _register(subparsers, parent)
