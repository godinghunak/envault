"""Rename or alias keys across env versions."""
from envault.vault import load_manifest, add_version, get_version
from envault.export import export_latest, export_version
from envault.diff import parse_env


def rename_key(vault_dir: str, old_key: str, new_key: str, version: int = None) -> str:
    """Return new env content with old_key renamed to new_key."""
    if version is not None:
        content = export_version(vault_dir, version)
    else:
        content = export_latest(vault_dir)
    lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith('#') or '=' not in stripped:
            lines.append(line)
            continue
        k, _, v = stripped.partition('=')
        if k.strip() == old_key:
            lines.append(f"{new_key}={v}")
        else:
            lines.append(line)
    return '\n'.join(lines) + '\n'


def apply_rename(vault_dir: str, password: str, old_key: str, new_key: str,
                 version: int = None) -> int:
    """Rename key and push a new version. Returns new version number."""
    new_content = rename_key(vault_dir, old_key, new_key, version)
    return add_version(vault_dir, password, new_content.encode())


def list_keys(vault_dir: str, version: int = None) -> list:
    """Return sorted list of keys in the given (or latest) version."""
    if version is not None:
        content = export_version(vault_dir, version)
    else:
        content = export_latest(vault_dir)
    return sorted(parse_env(content).keys())
