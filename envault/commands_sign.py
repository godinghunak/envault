"""CLI commands for signing and verifying vault versions."""
import argparse
from pathlib import Path

from envault.vault import load_manifest, _vault_path
from envault.env_sign import sign_version, verify_version, get_signature_entry, load_signatures


def _latest_version(vault_dir: str) -> int:
    m = load_manifest(vault_dir)
    versions = m.get("versions", [])
    if not versions:
        raise ValueError("No versions in vault.")
    return max(versions)


def _read_encrypted(vault_dir: str, version: int) -> bytes:
    p = _vault_path(vault_dir) / f"v{version}.enc"
    if not p.exists():
        raise FileNotFoundError(f"Encrypted file for version {version} not found.")
    return p.read_bytes()


def cmd_sign(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    version = args.version if args.version else _latest_version(vault_dir)
    data = _read_encrypted(vault_dir, version)
    sig = sign_version(vault_dir, version, data, args.secret)
    print(f"Signed version {version}: {sig[:16]}...")


def cmd_verify(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    version = args.version if args.version else _latest_version(vault_dir)
    data = _read_encrypted(vault_dir, version)
    try:
        valid = verify_version(vault_dir, version, data, args.secret)
    except KeyError as e:
        print(f"Error: {e}")
        return
    if valid:
        print(f"Version {version} signature is VALID.")
    else:
        print(f"Version {version} signature is INVALID — possible tampering!")


def cmd_sign_list(args: argparse.Namespace) -> None:
    sigs = load_signatures(args.vault_dir)
    if not sigs:
        print("No signatures recorded.")
        return
    for ver, entry in sorted(sigs.items(), key=lambda x: int(x[0])):
        print(f"  v{ver}  {entry['signature'][:16]}...  signed_at={entry['signed_at']}")


def register(subparsers, common_args) -> None:
    p_sign = subparsers.add_parser("sign", help="Sign a vault version")
    common_args(p_sign)
    p_sign.add_argument("--version", type=int, default=None)
    p_sign.add_argument("--secret", required=True, help="HMAC secret")
    p_sign.set_defaults(func=cmd_sign)

    p_verify = subparsers.add_parser("verify", help="Verify a vault version signature")
    common_args(p_verify)
    p_verify.add_argument("--version", type=int, default=None)
    p_verify.add_argument("--secret", required=True, help="HMAC secret")
    p_verify.set_defaults(func=cmd_verify)

    p_list = subparsers.add_parser("sign-list", help="List all signatures")
    common_args(p_list)
    p_list.set_defaults(func=cmd_sign_list)
