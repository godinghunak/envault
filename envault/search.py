"""Search across vault versions for keys or values."""

from envault.vault import load_manifest, _vault_path
from envault.crypto import decrypt_file
from envault.diff import parse_env


def search_key(vault_dir: str, password: str, pattern: str) -> list[dict]:
    """Search all versions for env keys matching pattern. Returns list of matches."""
    import fnmatch
    manifest = load_manifest(vault_dir)
    results = []
    for entry in manifest.get("versions", []):
        version = entry["version"]
        enc_path = _vault_path(vault_dir) / entry["file"]
        try:
            content = decrypt_file(str(enc_path), password)
            env = parse_env(content.decode())
        except Exception:
            continue
        for key, value in env.items():
            if fnmatch.fnmatch(key.lower(), pattern.lower()):
                results.append({"version": version, "key": key, "value": value})
    return results


def search_value(vault_dir: str, password: str, pattern: str) -> list[dict]:
    """Search all versions for env values matching pattern."""
    import fnmatch
    manifest = load_manifest(vault_dir)
    results = []
    for entry in manifest.get("versions", []):
        version = entry["version"]
        enc_path = _vault_path(vault_dir) / entry["file"]
        try:
            content = decrypt_file(str(enc_path), password)
            env = parse_env(content.decode())
        except Exception:
            continue
        for key, value in env.items():
            if fnmatch.fnmatch(value.lower(), pattern.lower()):
                results.append({"version": version, "key": key, "value": value})
    return results


def search_in_version(vault_dir: str, password: str, version: int, pattern: str) -> dict:
    """Search a specific version for a key pattern."""
    import fnmatch
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    entry = next((e for e in versions if e["version"] == version), None)
    if entry is None:
        raise ValueError(f"Version {version} not found")
    enc_path = _vault_path(vault_dir) / entry["file"]
    content = decrypt_file(str(enc_path), password)
    env = parse_env(content.decode())
    return {k: v for k, v in env.items() if fnmatch.fnmatch(k.lower(), pattern.lower())}
