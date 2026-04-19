"""CLI commands for patching vault versions."""
from envault.env_patch import patch_version, patch_latest
from envault.vault import load_manifest


def _parse_kv_args(pairs):
    result = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise ValueError(f"Invalid key=value pair: {pair!r}")
        k, v = pair.split("=", 1)
        result[k.strip()] = v.strip()
    return result


def cmd_patch(args):
    vault_dir = args.vault_dir
    password = args.password
    updates = _parse_kv_args(getattr(args, "set", None))
    removals = getattr(args, "remove", None) or []

    if not updates and not removals:
        print("Nothing to patch: provide --set or --remove.")
        return

    if getattr(args, "version", None) is not None:
        new_ver = patch_version(vault_dir, password, args.version, updates, removals)
    else:
        new_ver = patch_latest(vault_dir, password, updates, removals)

    print(f"Patched successfully. New version: {new_ver}")


def register(subparsers):
    p = subparsers.add_parser("patch", help="Patch keys in a vault version")
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--password", required=True, help="Vault password")
    p.add_argument("--version", type=int, default=None, help="Version to patch (default: latest)")
    p.add_argument("--set", nargs="+", metavar="KEY=VALUE", help="Key-value pairs to set")
    p.add_argument("--remove", nargs="+", metavar="KEY", help="Keys to remove")
    p.set_defaults(func=cmd_patch)
