"""Patch CLI parser to add profile subcommands."""
from envault.commands_profiles import (
    cmd_profile_add, cmd_profile_remove, cmd_profile_list, cmd_profile_show
)


def register(subparsers, global_vault_dir):
    p = subparsers.add_parser("profile", help="Manage named env profiles")
    sub = p.add_subparsers(dest="profile_cmd")

    pa = sub.add_parser("add", help="Add a profile")
    pa.add_argument("name")
    pa.add_argument("env_file")

    pr = sub.add_parser("remove", help="Remove a profile")
    pr.add_argument("name")

    sub.add_parser("list", help="List profiles")

    ps = sub.add_parser("show", help="Show profile details")
    ps.add_argument("name")

    def dispatch(args):
        args.vault_dir = global_vault_dir
        cmds = {
            "add": cmd_profile_add,
            "remove": cmd_profile_remove,
            "list": cmd_profile_list,
            "show": cmd_profile_show,
        }
        fn = cmds.get(args.profile_cmd)
        if fn:
            fn(args)
        else:
            p.print_help()

    p.set_defaults(func=dispatch)
