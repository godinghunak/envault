"""CLI commands for batch decryption."""

import argparse
from envault.env_decrypt_all import decrypt_all_versions, decrypt_version, list_decryptable_versions


def cmd_decrypt_all(args: argparse.Namespace) -> None:
    """Decrypt and print all versions."""
    results = decrypt_all_versions(args.vault_dir, args.password)
    if not results:
        print("No versions found in vault.")
        return
    for version, plaintext in results:
        print(f"=== Version {version} ===")
        print(plaintext)
        print()


def cmd_decrypt_version(args: argparse.Namespace) -> None:
    """Decrypt and print a specific version."""
    plaintext = decrypt_version(args.vault_dir, args.version, args.password)
    print(plaintext)


def cmd_decrypt_list(args: argparse.Namespace) -> None:
    """List versions decryptable with the given password."""
    versions = list_decryptable_versions(args.vault_dir, args.password)
    if not versions:
        print("No decryptable versions found.")
    else:
        print("Decryptable versions: " + ", ".join(str(v) for v in versions))


def register(subparsers, common_args):
    p_all = subparsers.add_parser("decrypt-all", help="Decrypt all versions")
    common_args(p_all)
    p_all.set_defaults(func=cmd_decrypt_all)

    p_ver = subparsers.add_parser("decrypt-version", help="Decrypt a specific version")
    common_args(p_ver)
    p_ver.add_argument("version", type=int, help="Version number to decrypt")
    p_ver.set_defaults(func=cmd_decrypt_version)

    p_list = subparsers.add_parser("decrypt-list", help="List decryptable versions")
    common_args(p_list)
    p_list.set_defaults(func=cmd_decrypt_list)
