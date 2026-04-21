"""Patch to register audit subcommands into the main CLI parser.

Call register(subparsers) from cli.py to add 'log' and 'log-clear' commands.
"""
from envault.commands_audit import cmd_log, cmd_log_clear

_VAULT_DIR_KWARGS = dict(
    dest="vault_dir",
    default=".",
    help="Path to vault root (default: current directory)",
)


def register(subparsers) -> None:
    """Add audit subcommands to an existing subparsers group.

    Commands registered:
      log        -- Display recorded audit events, optionally limited to the
                    last N entries.
      log-clear  -- Permanently remove all entries from the audit log.
    """
    # envault log
    p_log = subparsers.add_parser("log", help="Show audit log")
    p_log.add_argument(
        "--limit", type=int, default=None,
        help="Show only the last N events"
    )
    p_log.add_argument("--vault-dir", **_VAULT_DIR_KWARGS)
    p_log.set_defaults(func=cmd_log)

    # envault log-clear
    p_clear = subparsers.add_parser("log-clear", help="Clear audit log")
    p_clear.add_argument("--vault-dir", **_VAULT_DIR_KWARGS)
    p_clear.set_defaults(func=cmd_log_clear)
