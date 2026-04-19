"""Register batch-decrypt commands into the main CLI."""

from envault.commands_decrypt_all import register as _register


def register(subparsers, common_args):
    _register(subparsers, common_args)
