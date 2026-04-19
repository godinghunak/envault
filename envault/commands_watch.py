"""CLI command for watch mode."""
import argparse
from pathlib import Path

from envault.env_watch import watch_file, make_auto_push_handler
from envault.vault import init_vault


def cmd_watch(args: argparse.Namespace) -> None:
    vault_dir = Path(args.vault_dir)
    env_path = Path(args.file)

    if not env_path.exists():
        print(f"Error: {env_path} does not exist.")
        return

    init_vault(vault_dir)
    handler = make_auto_push_handler(vault_dir, args.password)

    print(f"[envault] watching {env_path} (interval={args.interval}s) — Ctrl+C to stop")
    try:
        watch_file(env_path, handler, interval=args.interval)
    except KeyboardInterrupt:
        print("\n[envault] watch stopped.")


def register(subparsers) -> None:
    p = subparsers.add_parser("watch", help="Watch a .env file and auto-push on change")
    p.add_argument("file", help="Path to the .env file to watch")
    p.add_argument("--password", required=True, help="Encryption password")
    p.add_argument(
        "--vault-dir", default=".envault", help="Vault directory (default: .envault)"
    )
    p.add_argument(
        "--interval", type=float, default=1.0, help="Poll interval in seconds (default: 1.0)"
    )
    p.set_defaults(func=cmd_watch)
