"""Register the resolve command with the main CLI parser."""
from envault.commands_resolve import register


def register_resolve(subparsers) -> None:
    register(subparsers)
