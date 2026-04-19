"""CLI commands for key renaming."""
import argparse
from envault.env_rename import apply_rename, list_keys
from envault.vault import load_manifest


def cmd_rename(args: argparse.Namespace) -> None:
    manifest = load_manifest(args.vault_dir)
    if not manifest.get('versions'):
        print('No versions found.')
        return
    version = getattr(args, 'version', None)
    new_ver = apply_rename(args.vault_dir, args.password, args.old_key, args.new_key, version)
    print(f"Renamed '{args.old_key}' -> '{args.new_key}', saved as version {new_ver}.")


def cmd_keys(args: argparse.Namespace) -> None:
    manifest = load_manifest(args.vault_dir)
    if not manifest.get('versions'):
        print('No versions found.')
        return
    version = getattr(args, 'version', None)
    keys = list_keys(args.vault_dir, version)
    if not keys:
        print('No keys found.')
    else:
        for k in keys:
            print(k)


def register(subparsers, common_parents):
    p_rename = subparsers.add_parser('rename', parents=common_parents,
                                     help='Rename a key and push new version')
    p_rename.add_argument('old_key', help='Key to rename')
    p_rename.add_argument('new_key', help='New key name')
    p_rename.add_argument('--version', type=int, default=None,
                          help='Base version (default: latest)')
    p_rename.set_defaults(func=cmd_rename)

    p_keys = subparsers.add_parser('keys', parents=common_parents,
                                   help='List keys in a version')
    p_keys.add_argument('--version', type=int, default=None,
                        help='Version to inspect (default: latest)')
    p_keys.set_defaults(func=cmd_keys)
