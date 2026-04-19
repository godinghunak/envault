"""Register placeholder commands with the main CLI parser."""

from __future__ import annotations
import argparse
from envault.commands_placeholder import register


def register_placeholder(subparsers: argparse._SubParsersAction) -> None:
    register(subparsers)
