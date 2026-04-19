"""CLI commands for key aliasing."""

from envault.env_alias import add_alias, remove_alias, resolve_alias, load_aliases


def cmd_alias_add(args) -> None:
    try:
        add_alias(args.vault_dir, args.alias, args.target)
        print(f"Alias '{args.alias}' -> '{args.target}' added.")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_alias_remove(args) -> None:
    try:
        remove_alias(args.vault_dir, args.alias)
        print(f"Alias '{args.alias}' removed.")
    except KeyError as e:
        print(f"Error: {e}")


def cmd_alias_list(args) -> None:
    aliases = load_aliases(args.vault_dir)
    if not aliases:
        print("No aliases defined.")
        return
    for alias, target in sorted(aliases.items()):
        print(f"  {alias} -> {target}")


def cmd_alias_resolve(args) -> None:
    result = resolve_alias(args.vault_dir, args.alias)
    if result == args.alias:
        print(f"'{args.alias}' is not aliased (resolves to itself).")
    else:
        print(f"'{args.alias}' resolves to '{result}'.")


def register(subparsers):
    p = subparsers.add_parser("alias", help="Manage key aliases")
    sp = p.add_subparsers(dest="alias_cmd")

    add_p = sp.add_parser("add", help="Add an alias")
    add_p.add_argument("alias")
    add_p.add_argument("target")
    add_p.set_defaults(func=cmd_alias_add)

    rm_p = sp.add_parser("remove", help="Remove an alias")
    rm_p.add_argument("alias")
    rm_p.set_defaults(func=cmd_alias_remove)

    ls_p = sp.add_parser("list", help="List all aliases")
    ls_p.set_defaults(func=cmd_alias_list)

    res_p = sp.add_parser("resolve", help="Resolve an alias to its target")
    res_p.add_argument("alias")
    res_p.set_defaults(func=cmd_alias_resolve)
