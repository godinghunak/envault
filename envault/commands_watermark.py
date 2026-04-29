"""CLI command handlers for watermark operations."""

import sys

from envault.env_watermark import (
    get_watermark,
    list_watermarks,
    remove_watermark,
    stamp,
    verify,
)
from envault.vault import load_manifest


def _latest_version(vault_dir: str) -> int:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        print("No versions found in vault.", file=sys.stderr)
        sys.exit(1)
    return max(versions)


def cmd_watermark_stamp(args) -> None:
    version = args.version if args.version is not None else _latest_version(args.vault_dir)
    mark = stamp(
        args.vault_dir,
        version=version,
        author=args.author,
        secret=args.secret,
        note=getattr(args, "note", "") or "",
    )
    print(f"Watermark stamped on version {version}.")
    print(f"  author : {args.author}")
    print(f"  mark   : {mark}")


def cmd_watermark_verify(args) -> None:
    version = args.version if args.version is not None else _latest_version(args.vault_dir)
    ok = verify(args.vault_dir, version=version, author=args.author, secret=args.secret)
    if ok:
        print(f"Watermark on version {version} is VALID.")
    else:
        print(f"Watermark on version {version} is INVALID or missing.", file=sys.stderr)
        sys.exit(1)


def cmd_watermark_show(args) -> None:
    version = args.version if args.version is not None else _latest_version(args.vault_dir)
    entry = get_watermark(args.vault_dir, version)
    if entry is None:
        print(f"No watermark found for version {version}.")
        return
    print(f"Version : {version}")
    print(f"Author  : {entry['author']}")
    print(f"Mark    : {entry['mark']}")
    print(f"Time    : {entry['ts']}")
    if entry.get("note"):
        print(f"Note    : {entry['note']}")


def cmd_watermark_list(args) -> None:
    entries = list_watermarks(args.vault_dir)
    if not entries:
        print("No watermarks recorded.")
        return
    for e in entries:
        note = f"  [{e['note']}]" if e.get("note") else ""
        print(f"v{e['version']}  {e['author']}  {e['ts']}{note}")


def cmd_watermark_remove(args) -> None:
    version = args.version if args.version is not None else _latest_version(args.vault_dir)
    removed = remove_watermark(args.vault_dir, version)
    if removed:
        print(f"Watermark removed from version {version}.")
    else:
        print(f"No watermark found for version {version}.")


def register(subparsers):
    p = subparsers.add_parser("watermark", help="Embed and verify watermarks on vault versions")
    sp = p.add_subparsers(dest="watermark_cmd", required=True)

    def _common(sub):
        sub.add_argument("--vault-dir", default=".vault")
        sub.add_argument("--version", type=int, default=None)

    s = sp.add_parser("stamp", help="Stamp a watermark on a version")
    _common(s)
    s.add_argument("--author", required=True)
    s.add_argument("--secret", required=True)
    s.add_argument("--note", default="")
    s.set_defaults(func=cmd_watermark_stamp)

    v = sp.add_parser("verify", help="Verify a watermark")
    _common(v)
    v.add_argument("--author", required=True)
    v.add_argument("--secret", required=True)
    v.set_defaults(func=cmd_watermark_verify)

    sh = sp.add_parser("show", help="Show watermark details for a version")
    _common(sh)
    sh.set_defaults(func=cmd_watermark_show)

    ls = sp.add_parser("list", help="List all watermarks")
    ls.add_argument("--vault-dir", default=".vault")
    ls.set_defaults(func=cmd_watermark_list)

    rm = sp.add_parser("remove", help="Remove a watermark")
    _common(rm)
    rm.set_defaults(func=cmd_watermark_remove)
