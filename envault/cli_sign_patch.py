"""Register sign/verify commands into the main CLI."""
from envault.commands_sign import register as _register


def register(subparsers) -> None:
    def common_args(p):
        p.add_argument(
            "--vault-dir",
            default=".",
            help="Path to the vault directory (default: current directory)",
        )

    _register(subparsers, common_args)
