"""CLI commands for password rotation."""

import argparse
from envault.vault import init_vault
from envault.env_rotate import rotate_password, rotate_single_version
from envault.audit import log_event


def cmd_rotate(args: argparse.Namespace) -> None:
    """Rotate the encryption password for vault versions."""
    vault_dir = args.vault_dir
    old_pw = args.old_password
    new_pw = args.new_password

    if args.version is not None:
        try:
            rotate_single_version(vault_dir, args.version, old_pw, new_pw)
            print(f"Rotated password for version {args.version}.")
            log_event(vault_dir, "rotate", {"version": args.version})
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except Exception:
            print("Error: old password is incorrect or data is corrupted.")
        return

    try:
        rotated = rotate_password(vault_dir, old_pw, new_pw)
    except Exception:
        print("Error: old password is incorrect or data is corrupted.")
        return

    if not rotated:
        print("No versions found to rotate.")
    else:
        print(f"Rotated {len(rotated)} version(s): {rotated}")
        log_event(vault_dir, "rotate", {"versions": rotated})


def register(subparsers) -> None:
    p = subparsers.add_parser("rotate", help="Re-encrypt vault versions with a new password")
    p.add_argument("old_password", help="Current encryption password")
    p.add_argument("new_password", help="New encryption password")
    p.add_argument("--version", type=int, default=None, help="Rotate a specific version only")
    p.add_argument("--vault-dir", default=".", help="Vault directory")
    p.set_defaults(func=cmd_rotate)
