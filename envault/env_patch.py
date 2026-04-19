"""Apply key-value patches to a specific vault version."""
from envault.vault import load_manifest, add_version
from envault.crypto import decrypt_file, encrypt_file
from envault.diff import parse_env


def patch_version(vault_dir: str, password: str, version: int, updates: dict, removals: list = None) -> int:
    """Apply key updates and removals to a version, saving as a new version."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions found in vault.")
    if version not in versions:
        raise ValueError(f"Version {version} does not exist.")

    from envault.vault import _vault_path
    import os
    enc_path = os.path.join(_vault_path(vault_dir), f"v{version}.enc")
    plaintext = decrypt_file(enc_path, password)
    env = parse_env(plaintext.decode())

    if removals:
        for key in removals:
            env.pop(key, None)

    env.update(updates)

    new_content = "".join(f"{k}={v}\n" for k, v in env.items())
    new_version = add_version(vault_dir, new_content.encode(), password)
    return new_version


def patch_latest(vault_dir: str, password: str, updates: dict, removals: list = None) -> int:
    """Apply patch to the latest version."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions found in vault.")
    latest = max(versions)
    return patch_version(vault_dir, password, latest, updates, removals)
