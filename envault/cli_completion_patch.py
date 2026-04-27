"""Register the completion command with the main CLI parser."""
from envault.commands_completion import register


def register_completion(subparsers) -> None:
    register(subparsers)
