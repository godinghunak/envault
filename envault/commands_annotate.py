"""CLI commands for env key annotations."""
from __future__ import annotations
import argparse
from envault.env_annotate import (
    set_annotation, remove_annotation, list_annotations, get_annotation
)
from envault.vault import load_manifest


def _latest_version(vault_dir: str) -> int:
    m = load_manifest(vault_dir)
    versions = m.get("versions", [])
    if not versions:
        raise RuntimeError("No versions found in vault.")
    return max(v["version"] for v in versions)


def cmd_annotate_set(args: argparse.Namespace) -> None:
    version = args.version if args.version is not None else _latest_version(args.vault_dir)
    set_annotation(args.vault_dir, version, args.key, args.note)
    print(f"Annotation set for '{args.key}' on version {version}.")


def cmd_annotate_remove(args: argparse.Namespace) -> None:
    version = args.version if args.version is not None else _latest_version(args.vault_dir)
    try:
        remove_annotation(args.vault_dir, version, args.key)
        print(f"Annotation removed for '{args.key}' on version {version}.")
    except KeyError as e:
        print(str(e))


def cmd_annotate_list(args: argparse.Namespace) -> None:
    version = args.version if args.version is not None else _latest_version(args.vault_dir)
    items = list_annotations(args.vault_dir, version)
    if not items:
        print(f"No annotations for version {version}.")
    else:
        print(f"Annotations for version {version}:")
        for key, note in items:
            print(f"  {key}: {note}")


def cmd_annotate_get(args: argparse.Namespace) -> None:
    version = args.version if args.version is not None else _latest_version(args.vault_dir)
    note = get_annotation(args.vault_dir, version, args.key)
    if note is None:
        print(f"No annotation for '{args.key}' in version {version}.")
    else:
        print(f"{args.key} (v{version}): {note}")


def register(subparsers, global_args):
    p = subparsers.add_parser("annotate", help="Manage key annotations")
    sp = p.add_subparsers(dest="annotate_cmd")

    def _add_version(parser):
        parser.add_argument("--version", type=int, default=None)

    s = sp.add_parser("set")
    s.add_argument("key"); s.add_argument("note"); _add_version(s)
    s.set_defaults(func=cmd_annotate_set)

    r = sp.add_parser("remove")
    r.add_argument("key"); _add_version(r)
    r.set_defaults(func=cmd_annotate_remove)

    ls = sp.add_parser("list"); _add_version(ls)
    ls.set_defaults(func=cmd_annotate_list)

    g = sp.add_parser("get")
    g.add_argument("key"); _add_version(g)
    g.set_defaults(func=cmd_annotate_get)
