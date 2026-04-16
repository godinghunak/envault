"""Patch to register audit subcommands into the main CLI parser.

Call register(subparsers) from cli.py to add 'log' and 'log-clear' commands.
"""
from envault.commands_audit import cmd_log, cmd_log_clear


def register(subparsers) -> None:
    """Add audit subcommands to an existing subparsers group."""
    # envault log
    p_log = subparsers.add_parser("log", help="Show audit log")
    p_log.add_argument(
        "--limit", type=int, default=None,
        help="Show only the last N events"
    )
    p_log.add_argument(
        "--vault-dir", dest="vault_dir", default=".",
        help="Path to vault root (default: current directory)"
    )
    p_log.set_defaults(func=cmd_log)

    # envault log-clear
    p_clear = subparsers.add_parser("log-clear", help="Clear audit log")
    p_clear.add_argument(
        "--vault-dir", dest="vault_dir", default=".",
        help="Path to vault root (default: current directory)"
    )
    p_clear.set_defaults(func=cmd_log_clear)
