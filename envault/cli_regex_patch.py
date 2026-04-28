"""Register the regex subcommand with the main CLI parser."""
from envault.commands_regex import register


def register_regex(subparsers) -> None:
    register(subparsers)
