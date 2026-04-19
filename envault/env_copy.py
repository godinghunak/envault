"""Copy keys from one version to another, optionally overwriting."""
from envault.vault import load_manifest, add_version
from envault.crypto import decrypt_file, encrypt
from envault.diff import parse_env


class CopyError(Exception):
    pass


def copy_keys(vault_dir, src_version, dst_version, keys, password, overwrite=False):
    """Copy specific keys from src_version into dst_version.
    Returns a new version number with the merged content.
    """
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    version_nums = [v["version"] for v in versions]

    if src_version not in version_nums:
        raise CopyError(f"Source version {src_version} not found")
    if dst_version not in version_nums:
        raise CopyError(f"Destination version {dst_version} not found")

    src_entry = next(v for v in versions if v["version"] == src_version)
    dst_entry = next(v for v in versions if v["version"] == dst_version)

    src_text = decrypt_file(src_entry["path"], password)
    dst_text = decrypt_file(dst_entry["path"], password)

    src_env = parse_env(src_text)
    dst_env = parse_env(dst_text)

    missing = [k for k in keys if k not in src_env]
    if missing:
        raise CopyError(f"Keys not found in source version: {', '.join(missing)}")

    conflicts = [k for k in keys if k in dst_env and not overwrite]
    if conflicts:
        raise CopyError(
            f"Keys already exist in destination (use overwrite=True): {', '.join(conflicts)}"
        )

    merged = dict(dst_env)
    for k in keys:
        merged[k] = src_env[k]

    new_text = "".join(f"{k}={v}\n" for k, v in merged.items())
    new_version = add_version(vault_dir, new_text.encode(), password)
    return new_version


def copy_all_keys(vault_dir, src_version, dst_version, password, overwrite=False):
    """Copy all keys from src_version into dst_version."""
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    version_nums = [v["version"] for v in versions]

    if src_version not in version_nums:
        raise CopyError(f"Source version {src_version} not found")

    src_entry = next(v for v in versions if v["version"] == src_version)
    src_text = decrypt_file(src_entry["path"], password)
    src_env = parse_env(src_text)

    return copy_keys(vault_dir, src_version, dst_version, list(src_env.keys()), password, overwrite)
