"""Register the deprecate command group with the main CLI parser."""

from envault.commands_deprecate import register


def register_deprecate(subparsers) -> None:
    register(subparsers)
