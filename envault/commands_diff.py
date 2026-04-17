"""CLI commands for diffing vault versions."""
from __future__ import annotations
import argparse
from envault.vault import load_manifest, _vault_path
from envault.crypto import decrypt_file
from envault.diff import parse_env, diff_envs, format_diff


def cmd_diff(args: argparse.Namespace) -> None:
    """Show diff between two versions (or latest two) of the env file."""
    manifest = load_manifest(args.vault_dir)
    versions = manifest.get("versions", [])

    if len(versions) < 2:
        print("Need at least 2 versions to diff.")
        return

    v_new_meta = versions[-1]
    v_old_meta = versions[-2]

    if args.v1 is not None and args.v2 is not None:
        by_num = {v["version"]: v for v in versions}
        if args.v1 not in by_num or args.v2 not in by_num:
            print(f"Version not found. Available: {sorted(by_num)}")
            return
        v_old_meta = by_num[args.v1]
        v_new_meta = by_num[args.v2]

    vault_dir = args.vault_dir
    old_path = _vault_path(vault_dir) / v_old_meta["filename"]
    new_path = _vault_path(vault_dir) / v_new_meta["filename"]

    old_content = decrypt_file(str(old_path), args.password).decode()
    new_content = decrypt_file(str(new_path), args.password).decode()

    old_env = parse_env(old_content)
    new_env = parse_env(new_content)

    diff = diff_envs(old_env, new_env)
    show_vals = getattr(args, "show_values", False)
    print(f"Diff v{v_old_meta['version']} -> v{v_new_meta['version']}:")
    print(format_diff(diff, show_values=show_vals))
