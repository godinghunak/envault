"""Register tag subcommands into the main CLI parser."""

from envault.commands_tags import cmd_tag_add, cmd_tag_remove, cmd_tag_list, cmd_tag_resolve


def register(subparsers):
    tag_parser = subparsers.add_parser("tag", help="Manage version tags")
    tag_sub = tag_parser.add_subparsers(dest="tag_cmd")

    p_add = tag_sub.add_parser("add", help="Add a tag to a version")
    p_add.add_argument("tag", help="Tag name")
    p_add.add_argument("--version", type=int, default=None, help="Version number (default: latest)")
    p_add.set_defaults(func=cmd_tag_add)

    p_rm = tag_sub.add_parser("remove", help="Remove a tag")
    p_rm.add_argument("tag", help="Tag name")
    p_rm.set_defaults(func=cmd_tag_remove)

    p_ls = tag_sub.add_parser("list", help="List all tags")
    p_ls.set_defaults(func=cmd_tag_list)

    p_res = tag_sub.add_parser("resolve", help="Resolve a tag to a version number")
    p_res.add_argument("tag", help="Tag name")
    p_res.set_defaults(func=cmd_tag_resolve)

    def tag_dispatch(args):
        if args.tag_cmd is None:
            tag_parser.print_help()
        else:
            args.func(args)

    tag_parser.set_defaults(func=tag_dispatch)
