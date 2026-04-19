"""CLI commands for managing vault version quotas."""

from envault.env_quota import set_quota, get_quota, clear_quota, check_quota
from envault.vault import load_manifest


def cmd_quota_set(args) -> None:
    try:
        max_v = int(args.max_versions)
    except ValueError:
        print("Error: max_versions must be an integer.")
        return
    set_quota(args.vault_dir, max_v)
    print(f"Quota set: max {max_v} versions.")


def cmd_quota_show(args) -> None:
    max_v = get_quota(args.vault_dir)
    manifest = load_manifest(args.vault_dir)
    current = len(manifest.get("versions", []))
    ok, _ = check_quota(args.vault_dir, current)
    status = "OK" if ok else "EXCEEDED"
    print(f"Max versions : {max_v}")
    print(f"Current      : {current}")
    print(f"Status       : {status}")


def cmd_quota_clear(args) -> None:
    clear_quota(args.vault_dir)
    print("Quota cleared (default limit restored).")


def register(subparsers, common_args) -> None:
    p_quota = subparsers.add_parser("quota", help="Manage version quota")
    quota_sub = p_quota.add_subparsers(dest="quota_cmd")

    p_set = quota_sub.add_parser("set", help="Set max versions")
    common_args(p_set)
    p_set.add_argument("max_versions", help="Maximum number of versions to keep")
    p_set.set_defaults(func=cmd_quota_set)

    p_show = quota_sub.add_parser("show", help="Show current quota and usage")
    common_args(p_show)
    p_show.set_defaults(func=cmd_quota_show)

    p_clear = quota_sub.add_parser("clear", help="Clear quota (restore default)")
    common_args(p_clear)
    p_clear.set_defaults(func=cmd_quota_clear)
