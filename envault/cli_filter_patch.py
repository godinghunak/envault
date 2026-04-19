"""Register filter commands with the main CLI parser."""
from __future__ import annotations
import argparse
from envault.commands_filter import register


def register_filter(subparsers: argparse._SubParsersAction) -> None:
    register(subparsers)
