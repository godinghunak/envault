"""CLI command handlers for the bookmark feature."""

from __future__ import annotations

from envault.env_bookmark import (
    add_bookmark,
    list_bookmarks,
    remove_bookmark,
    resolve_bookmark,
)
from envault.vault import load_manifest


def _latest_version(vault_dir: str) -> int:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions found in vault.")
    return max(v["version"] for v in versions)


def cmd_bookmark_add(args) -> None:
    vault_dir = args.vault_dir
    version = args.version if args.version else _latest_version(vault_dir)
    try:
        add_bookmark(vault_dir, args.name, version)
        print(f"Bookmark '{args.name}' -> version {version} saved.")
    except (ValueError, KeyError) as exc:
        print(f"Error: {exc}")


def cmd_bookmark_remove(args) -> None:
    try:
        remove_bookmark(args.vault_dir, args.name)
        print(f"Bookmark '{args.name}' removed.")
    except KeyError as exc:
        print(f"Error: {exc}")


def cmd_bookmark_list(args) -> None:
    entries = list_bookmarks(args.vault_dir)
    if not entries:
        print("No bookmarks defined.")
        return
    for name, version in entries:
        print(f"  {name:20s}  ->  v{version}")


def cmd_bookmark_resolve(args) -> None:
    version = resolve_bookmark(args.vault_dir, args.name)
    if version is None:
        print(f"Bookmark '{args.name}' not found.")
    else:
        print(f"{version}")


def register(subparsers) -> None:
    p = subparsers.add_parser("bookmark", help="Manage version bookmarks")
    sub = p.add_subparsers(dest="bookmark_cmd")

    p_add = sub.add_parser("add", help="Add a bookmark")
    p_add.add_argument("name", help="Bookmark label")
    p_add.add_argument("--version", type=int, default=None, help="Version to bookmark (default: latest)")
    p_add.set_defaults(func=cmd_bookmark_add)

    p_rm = sub.add_parser("remove", help="Remove a bookmark")
    p_rm.add_argument("name", help="Bookmark label")
    p_rm.set_defaults(func=cmd_bookmark_remove)

    p_ls = sub.add_parser("list", help="List all bookmarks")
    p_ls.set_defaults(func=cmd_bookmark_list)

    p_res = sub.add_parser("resolve", help="Resolve bookmark to version number")
    p_res.add_argument("name", help="Bookmark label")
    p_res.set_defaults(func=cmd_bookmark_resolve)
