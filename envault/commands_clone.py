"""CLI commands for cloning vault versions to .env files."""
import argparse
from envault.env_clone import clone_version_to_file, clone_latest_to_file, list_clone_targets


def cmd_clone(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    dest = args.dest
    password = args.password
    version = args.version if hasattr(args, "version") else None

    if version is not None:
        cloned = clone_version_to_file(vault_dir, version, dest, password)
        print(f"Cloned version {cloned} -> {dest}")
    else:
        cloned = clone_latest_to_file(vault_dir, dest, password)
        print(f"Cloned latest (v{cloned}) -> {dest}")


def cmd_clone_list(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    versions = list_clone_targets(vault_dir)
    if not versions:
        print("No versions available to clone.")
    else:
        print("Cloneable versions:")
        for v in versions:
            print(f"  v{v}")


def register(subparsers) -> None:
    p = subparsers.add_parser("clone", help="Clone a vault version to a .env file")
    sp = p.add_subparsers(dest="clone_cmd")

    p_get = sp.add_parser("get", help="Clone a version to a file")
    p_get.add_argument("dest", help="Destination file path")
    p_get.add_argument("--version", type=int, default=None, help="Version to clone (default: latest)")
    p_get.add_argument("--vault-dir", default=".envault")
    p_get.add_argument("--password", required=True)
    p_get.set_defaults(func=cmd_clone)

    p_list = sp.add_parser("list", help="List cloneable versions")
    p_list.add_argument("--vault-dir", default=".envault")
    p_list.set_defaults(func=cmd_clone_list)
