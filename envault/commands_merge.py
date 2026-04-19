"""CLI commands for env merge."""
import argparse
from envault.env_merge import merge_versions, format_merged
from envault.vault import load_manifest


def cmd_merge(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    password = args.password
    manifest = load_manifest(vault_dir)
    versions = [v["version"] for v in manifest.get("versions", [])]

    if len(versions) < 2:
        print("Need at least 2 versions to merge.")
        return

    base_v = args.base
    our_v = args.ours
    their_v = args.theirs

    for v in (base_v, our_v, their_v):
        if v not in versions:
            print(f"Version {v} not found in vault.")
            return

    result = merge_versions(vault_dir, base_v, our_v, their_v, password)

    if result.has_conflicts:
        print(f"Merge completed with {len(result.conflicts)} conflict(s):")
        for c in result.conflicts:
            print(f"  {c}")
        print("Merged result (ours kept for conflicts):")
    else:
        print("Merge completed with no conflicts.")

    output = format_merged(result.merged)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Written to {args.output}")
    else:
        print(output)


def register(subparsers):
    p = subparsers.add_parser("merge", help="Three-way merge two env versions")
    p.add_argument("--base", type=int, required=True, help="Base version number")
    p.add_argument("--ours", type=int, required=True, help="Our version number")
    p.add_argument("--theirs", type=int, required=True, help="Their version number")
    p.add_argument("--output", "-o", default=None, help="Write merged result to file")
    p.set_defaults(func=cmd_merge)
