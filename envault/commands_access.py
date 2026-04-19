"""CLI commands for access control."""
from envault.env_access import grant, revoke, list_grants, can_access


def cmd_access_grant(args) -> None:
    grant(args.vault_dir, args.role, args.key)
    print(f"Granted '{args.role}' access to '{args.key}'.")


def cmd_access_revoke(args) -> None:
    revoke(args.vault_dir, args.role, args.key)
    print(f"Revoked '{args.role}' access to '{args.key}'.")


def cmd_access_list(args) -> None:
    keys = list_grants(args.vault_dir, args.role)
    if not keys:
        print(f"No keys granted to role '{args.role}'.")
    else:
        print(f"Role '{args.role}' can access:")
        for k in keys:
            print(f"  {k}")


def cmd_access_check(args) -> None:
    ok = can_access(args.vault_dir, args.role, args.key)
    status = "ALLOWED" if ok else "DENIED"
    print(f"Access for '{args.role}' to '{args.key}': {status}")


def register(subparsers, vault_dir_default="."):
    p = subparsers.add_parser("access", help="Manage key access control")
    p.add_argument("--vault-dir", default=vault_dir_default)
    sub = p.add_subparsers(dest="access_cmd", required=True)

    g = sub.add_parser("grant", help="Grant role access to a key")
    g.add_argument("role")
    g.add_argument("key")
    g.set_defaults(func=cmd_access_grant)

    r = sub.add_parser("revoke", help="Revoke role access to a key")
    r.add_argument("role")
    r.add_argument("key")
    r.set_defaults(func=cmd_access_revoke)

    ls = sub.add_parser("list", help="List keys accessible by role")
    ls.add_argument("role")
    ls.set_defaults(func=cmd_access_list)

    ch = sub.add_parser("check", help="Check if role can access key")
    ch.add_argument("role")
    ch.add_argument("key")
    ch.set_defaults(func=cmd_access_check)
