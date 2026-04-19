"""CLI commands for vault backup and restore."""

import argparse
from pathlib import Path
from datetime import datetime

from envault.env_backup import create_backup, restore_backup, backup_info


def cmd_backup(args: argparse.Namespace) -> None:
    vault_dir = getattr(args, "vault_dir", ".envault")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = getattr(args, "output", None) or f"envault_backup_{timestamp}.tar.gz"

    try:
        path = create_backup(vault_dir, dest)
        print(f"Backup created: {path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")


def cmd_restore(args: argparse.Namespace) -> None:
    backup_path = args.backup_file
    dest_dir = getattr(args, "dest", None) or ".envault"
    overwrite = getattr(args, "overwrite", False)

    try:
        path = restore_backup(backup_path, dest_dir, overwrite=overwrite)
        print(f"Vault restored to: {path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except FileExistsError as e:
        print(f"Error: {e}")


def cmd_backup_info(args: argparse.Namespace) -> None:
    backup_path = args.backup_file

    try:
        info = backup_info(backup_path)
        print(f"Path:    {info['path']}")
        print(f"Size:    {info['size_bytes']} bytes")
        print(f"Created: {info['created']}")
        print(f"Files ({len(info['files'])}):")
        for f in info["files"]:
            print(f"  {f}")
    except FileNotFoundError as e:
        print(f"Error: {e}")


def register(subparsers) -> None:
    p_backup = subparsers.add_parser("backup", help="Create a vault backup")
    p_backup.add_argument("--output", help="Output .tar.gz path")
    p_backup.add_argument("--vault-dir", dest="vault_dir", default=".envault")
    p_backup.set_defaults(func=cmd_backup)

    p_restore = subparsers.add_parser("restore", help="Restore vault from backup")
    p_restore.add_argument("backup_file", help="Path to .tar.gz backup")
    p_restore.add_argument("--dest", default=".envault", help="Restore destination")
    p_restore.add_argument("--overwrite", action="store_true")
    p_restore.set_defaults(func=cmd_restore)

    p_info = subparsers.add_parser("backup-info", help="Show backup archive info")
    p_info.add_argument("backup_file", help="Path to .tar.gz backup")
    p_info.set_defaults(func=cmd_backup_info)
