"""Register the drift command with the main CLI parser."""
from envault.commands_drift import register


def register_drift(subparsers) -> None:
    register(subparsers)
