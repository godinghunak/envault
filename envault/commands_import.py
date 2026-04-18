"""CLI commands for importing .env data into the vault."""
from __future__ import annotations
import argparse

from envault.import_env import import_from_file, import_from_string, import_from_env


def cmd_import(args: argparse.Namespace) -> None:
    source = getattr(args, "source", "file")
    strict = getattr(args, "strict", False)

    if source == "file":
        if not args.path:
            print("Error: --path required for file import")
            return
        try:
            version = import_from_file(args.vault_dir, args.path, args.password, strict=strict)
            print(f"Imported '{args.path}' as version {version}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Lint failed:\n{e}")

    elif source == "env":
        keys = args.keys.split(",") if getattr(args, "keys", None) else None
        version = import_from_env(args.vault_dir, keys, args.password)
        print(f"Imported from environment as version {version}")

    elif source == "string":
        if not getattr(args, "content", None):
            print("Error: --content required for string import")
            return
        try:
            version = import_from_string(args.vault_dir, args.content, args.password, strict=strict)
            print(f"Imported content as version {version}")
        except ValueError as e:
            print(f"Lint failed:\n{e}")
    else:
        print(f"Unknown import source: {source}")
