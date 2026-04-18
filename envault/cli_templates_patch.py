from envault.templates_commands import (
    cmd_template_add,
    cmd_template_remove,
    cmd_template_list,
    cmd_template_show,
    cmd_template_render,
)


def dispatch(args):
    cmds = {
        "add": cmd_template_add,
        "remove": cmd_template_remove,
        "list": cmd_template_list,
        "show": cmd_template_show,
        "render": cmd_template_render,
    }
    fn = cmds.get(args.template_cmd)
    if fn:
        fn(args)
    else:
        print("Unknown template subcommand.")


def register(subparsers):
    p = subparsers.add_parser("template", help="Manage env templates")
    p.set_defaults(func=dispatch)
    sub = p.add_subparsers(dest="template_cmd")

    add_p = sub.add_parser("add", help="Add a template")
    add_p.add_argument("name")
    add_p.add_argument("--keys", help="Comma-separated list of keys")

    rm_p = sub.add_parser("remove", help="Remove a template")
    rm_p.add_argument("name")

    sub.add_parser("list", help="List templates")

    show_p = sub.add_parser("show", help="Show template keys")
    show_p.add_argument("name")

    render_p = sub.add_parser("render", help="Render a template against a version")
    render_p.add_argument("name")
    render_p.add_argument("--version", type=int, default=None)
    render_p.add_argument("--password", required=True)
