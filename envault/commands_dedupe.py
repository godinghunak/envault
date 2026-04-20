"""CLI commands for detecting and removing duplicate keys."""
import argparse
from envault.vault import load_manifest, _vault_path
from envault.crypto import decrypt_file
from envault.env_dedupe import find_duplicates, dedupe_env
from envault.export import export_latest, export_version
from envault import vault


def _latest_version(vault_dir: str) -> int:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions in vault.")
    return max(v["version"] for v in versions)


def cmd_dedupe_check(args: argparse.Namespace) -> None:
    """Report duplicate keys in a vault version or a plain file."""
    if hasattr(args, "file") and args.file:
        with open(args.file) as f:
            text = f.read()
        source = args.file
    else:
        version = getattr(args, "version", None)
        if version is None:
            version = _latest_version(args.vault_dir)
        text = export_version(args.vault_dir, version, args.password)
        source = f"version {version}"

    dupes = find_duplicates(text)
    if not dupes:
        print(f"No duplicate keys found in {source}.")
    else:
        print(f"Duplicate keys in {source}:")
        for d in dupes:
            vals = " | ".join(d.values)
            print(f"  {d}  values: [{vals}]")


def cmd_dedupe_fix(args: argparse.Namespace) -> None:
    """Push a new vault version with duplicates removed."""
    version = getattr(args, "version", None)
    if version is None:
        version = _latest_version(args.vault_dir)

    text = export_version(args.vault_dir, version, args.password)
    dupes = find_duplicates(text)
    if not dupes:
        print("No duplicates found; nothing to do.")
        return

    keep = getattr(args, "keep", "last")
    cleaned = dedupe_env(text, keep=keep)

    import tempfile, os
    from envault.commands import cmd_push

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as tmp:
        tmp.write(cleaned)
        tmp_path = tmp.name

    try:
        push_args = argparse.Namespace(
            vault_dir=args.vault_dir,
            env_file=tmp_path,
            password=args.password,
        )
        cmd_push(push_args)
        removed = len(dupes)
        print(f"Removed {removed} duplicate key(s); new version pushed.")
    finally:
        os.unlink(tmp_path)


def register(subparsers) -> None:
    p_check = subparsers.add_parser("dedupe-check", help="Find duplicate keys")
    p_check.add_argument("--vault-dir", default=".envault")
    p_check.add_argument("--password", required=True)
    p_check.add_argument("--version", type=int, default=None)
    p_check.add_argument("--file", default=None, help="Check a plain .env file instead")
    p_check.set_defaults(func=cmd_dedupe_check)

    p_fix = subparsers.add_parser("dedupe-fix", help="Remove duplicate keys and push")
    p_fix.add_argument("--vault-dir", default=".envault")
    p_fix.add_argument("--password", required=True)
    p_fix.add_argument("--version", type=int, default=None)
    p_fix.add_argument("--keep", choices=["first", "last"], default="last")
    p_fix.set_defaults(func=cmd_dedupe_fix)
