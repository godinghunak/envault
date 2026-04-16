"""CLI entry point for envault using argparse."""

import argparse
import getpass
import sys

from envault.commands import cmd_init, cmd_push, cmd_pull, cmd_list


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envault",
        description="Encrypt and version-control .env files.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize a new vault in the current directory.")

    push_p = sub.add_parser("push", help="Encrypt and push a .env file to the vault.")
    push_p.add_argument("env_file", nargs="?", default=".env", help="Path to .env file (default: .env)")
    push_p.add_argument("--label", default=None, help="Optional version label.")

    pull_p = sub.add_parser("pull", help="Decrypt and pull a .env file from the vault.")
    pull_p.add_argument("output_file", nargs="?", default=".env", help="Output path (default: .env)")
    pull_p.add_argument("--version", type=int, default=None, dest="version_id", help="Version ID to pull.")

    sub.add_parser("list", help="List all stored versions.")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        print(cmd_init())

    elif args.command == "push":
        password = getpass.getpass("Encryption password: ")
        print(cmd_push(args.env_file, password, label=args.label))

    elif args.command == "pull":
        password = getpass.getpass("Decryption password: ")
        try:
            print(cmd_pull(args.output_file, password, version_id=args.version_id))
        except (KeyError, RuntimeError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "list":
        versions = cmd_list()
        if not versions:
            print("No versions found.")
        else:
            for v in versions:
                print(f"  [{v['id']}] {v['label']}  —  {v['created_at']}")


if __name__ == "__main__":
    main()
