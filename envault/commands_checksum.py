"""CLI commands for checksum recording and verification."""

import argparse
from pathlib import Path

from envault.vault import load_manifest
from envault.env_checksum import record_checksum, verify_checksum, get_checksum, load_checksums


def _latest_version(vault_dir: Path) -> int:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions in vault.")
    return max(versions)


def cmd_checksum_record(args: argparse.Namespace) -> None:
    vault_dir = Path(args.vault_dir)
    version = args.version if args.version is not None else _latest_version(vault_dir)
    checksum = record_checksum(vault_dir, version, args.password)
    print(f"Recorded checksum for v{version}: {checksum}")


def cmd_checksum_verify(args: argparse.Namespace) -> None:
    vault_dir = Path(args.vault_dir)
    version = args.version if args.version is not None else _latest_version(vault_dir)
    try:
        ok = verify_checksum(vault_dir, version, args.password)
    except KeyError as exc:
        print(f"Error: {exc}")
        return
    if ok:
        print(f"v{version}: checksum OK")
    else:
        print(f"v{version}: checksum MISMATCH — file may have been tampered with")


def cmd_checksum_show(args: argparse.Namespace) -> None:
    vault_dir = Path(args.vault_dir)
    version = args.version if args.version is not None else _latest_version(vault_dir)
    entry = get_checksum(vault_dir, version)
    if entry is None:
        print(f"No checksum recorded for v{version}.")
    else:
        print(f"v{version} [{entry['algorithm']}]: {entry['checksum']}")


def cmd_checksum_list(args: argparse.Namespace) -> None:
    vault_dir = Path(args.vault_dir)
    data = load_checksums(vault_dir)
    if not data:
        print("No checksums recorded.")
        return
    for ver, entry in sorted(data.items(), key=lambda x: int(x[0])):
        print(f"v{ver} [{entry['algorithm']}]: {entry['checksum']}")


def register(subparsers, common_args) -> None:
    p = subparsers.add_parser("checksum", help="Manage version checksums")
    sub = p.add_subparsers(dest="checksum_cmd", required=True)

    for name, fn, help_text in [
        ("record", cmd_checksum_record, "Record checksum for a version"),
        ("verify", cmd_checksum_verify, "Verify checksum for a version"),
        ("show",   cmd_checksum_show,   "Show stored checksum for a version"),
        ("list",   cmd_checksum_list,   "List all recorded checksums"),
    ]:
        sp = sub.add_parser(name, help=help_text)
        common_args(sp)
        if name != "list":
            sp.add_argument("--version", type=int, default=None)
        sp.set_defaults(func=fn)
