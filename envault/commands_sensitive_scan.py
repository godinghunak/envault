"""CLI command for scanning vault versions for sensitive values."""

import argparse
from envault.vault import load_manifest, _vault_path
from envault.crypto import decrypt_file
from envault.diff import parse_env
from envault.env_sensitive_scan import scan_versions, format_findings


def _load_all_versions(vault_dir: str, password: str) -> dict:
    """Decrypt and parse all versions from the vault."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    result = {}
    for entry in versions:
        ver = entry["version"]
        path = _vault_path(vault_dir) / entry["filename"]
        try:
            plaintext = decrypt_file(str(path), password)
            result[ver] = parse_env(plaintext.decode())
        except Exception:
            # Skip versions that cannot be decrypted
            pass
    return result


def cmd_sensitive_scan(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    password = args.password

    try:
        versions = _load_all_versions(vault_dir, password)
    except FileNotFoundError:
        print("Vault not initialised. Run `envault init` first.")
        return

    if not versions:
        print("No versions found in vault.")
        return

    if hasattr(args, 'version') and args.version is not None:
        ver = args.version
        if ver not in versions:
            print(f"Version {ver} not found.")
            return
        versions = {ver: versions[ver]}

    findings = scan_versions(versions)
    print(format_findings(findings))


def register(subparsers) -> None:
    p = subparsers.add_parser(
        "sensitive-scan",
        help="Scan vault versions for high-entropy sensitive values",
    )
    p.add_argument("--version", type=int, default=None,
                   help="Scan a specific version only (default: all)")
    p.add_argument("--vault-dir", default=".envault",
                   help="Path to vault directory")
    p.add_argument("--password", required=True,
                   help="Decryption password")
    p.set_defaults(func=cmd_sensitive_scan)
