"""CLI commands for copying keys between versions."""
from envault.env_copy import copy_keys, copy_all_keys, CopyError


def cmd_copy(args):
    keys = args.keys.split(",") if args.keys else None
    try:
        if keys:
            new_version = copy_keys(
                args.vault_dir,
                args.src,
                args.dst,
                keys,
                args.password,
                overwrite=args.overwrite,
            )
        else:
            new_version = copy_all_keys(
                args.vault_dir,
                args.src,
                args.dst,
                args.password,
                overwrite=args.overwrite,
            )
        label = f"keys [{args.keys}]" if args.keys else "all keys"
        print(f"Copied {label} from v{args.src} into v{args.dst} -> new version v{new_version}")
    except CopyError as e:
        print(f"Error: {e}")


def register(subparsers):
    p = subparsers.add_parser("copy", help="Copy keys from one version to another")
    p.add_argument("src", type=int, help="Source version number")
    p.add_argument("dst", type=int, help="Destination version number")
    p.add_argument("--keys", default=None, help="Comma-separated list of keys to copy (default: all)")
    p.add_argument("--password", required=True, help="Vault password")
    p.add_argument("--vault-dir", default=".envault", dest="vault_dir")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing keys in destination")
    p.set_defaults(func=cmd_copy)
