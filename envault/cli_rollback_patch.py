"""Register rollback subcommands into the main CLI parser."""

from envault.commands_rollback import cmd_rollback, cmd_versions


def register(subparsers, common_args):
    # rollback subcommand
    p_rollback = subparsers.add_parser("rollback", help="Restore a previous version of an env file")
    common_args(p_rollback)
    p_rollback.add_argument("name", help="Name of the env file (e.g. .env)")
    p_rollback.add_argument("version", type=int, help="Version number to restore")
    p_rollback.add_argument("--output", default=None, help="Output file path (default: .env.rollback.vN)")
    p_rollback.add_argument("--password", required=True, help="Decryption password")
    p_rollback.set_defaults(func=cmd_rollback)

    # versions subcommand
    p_versions = subparsers.add_parser("versions", help="List stored versions for an env file")
    common_args(p_versions)
    p_versions.add_argument("name", help="Name of the env file")
    p_versions.set_defaults(func=cmd_versions)
