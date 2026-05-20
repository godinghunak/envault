"""CLI command for env similarity comparison."""
from __future__ import annotations
import argparse

from envault.vault import load_manifest
from envault.export import export_version
from envault.diff import parse_env
from envault.env_similarity import compare_dicts, similarity_score


def cmd_similarity(args: argparse.Namespace) -> None:
    manifest = load_manifest(args.vault_dir)
    versions = manifest.get("versions", [])

    if len(versions) < 2:
        print("Need at least two versions to compare.")
        return

    v_a = args.version_a if args.version_a is not None else versions[-2]
    v_b = args.version_b if args.version_b is not None else versions[-1]

    if v_a not in versions:
        print(f"Version {v_a} not found.")
        return
    if v_b not in versions:
        print(f"Version {v_b} not found.")
        return

    text_a = export_version(args.vault_dir, v_a, args.password)
    text_b = export_version(args.vault_dir, v_b, args.password)

    dict_a = parse_env(text_a)
    dict_b = parse_env(text_b)

    result = compare_dicts(dict_a, dict_b, version_a=v_a, version_b=v_b)
    score = similarity_score(result)

    print(str(result))
    print(f"  Overall score   : {score:.1%}")

    if args.show_keys:
        if result.changed_keys:
            print("\nChanged keys:")
            for k in result.changed_keys:
                print(f"  ~ {k}")
        if result.only_in_a:
            print(f"\nOnly in v{v_a}:")
            for k in result.only_in_a:
                print(f"  - {k}")
        if result.only_in_b:
            print(f"\nOnly in v{v_b}:")
            for k in result.only_in_b:
                print(f"  + {k}")


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("similarity", help="Compare similarity of two versions")
    p.add_argument("--vault-dir", default=".envault")
    p.add_argument("--password", required=True)
    p.add_argument("--version-a", type=int, default=None, dest="version_a")
    p.add_argument("--version-b", type=int, default=None, dest="version_b")
    p.add_argument("--show-keys", action="store_true", default=False)
    p.set_defaults(func=cmd_similarity)
