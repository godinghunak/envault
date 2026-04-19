"""Reorder keys in an env version by a given key list or alphabetically."""
from envault.vault import load_manifest, get_version, add_version
from envault.crypto import decrypt_file, encrypt_file


def reorder_env(env_text: str, key_order: list[str], alphabetical: bool = False) -> str:
    """Return env text with keys reordered.

    Keys in key_order come first (in that order); remaining keys follow.
    If alphabetical=True and key_order is empty, sort all keys.
    """
    lines = env_text.splitlines()
    pairs: dict[str, str] = {}
    meta: list[tuple[str | None, str]] = []  # (key_or_None, raw_line)

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            meta.append((None, line))
        elif "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            pairs[key] = line
            meta.append((key, line))
        else:
            meta.append((None, line))

    all_keys = list(pairs.keys())
    if alphabetical and not key_order:
        ordered_keys = sorted(all_keys)
    else:
        seen = set(key_order)
        ordered_keys = [k for k in key_order if k in pairs] + [
            k for k in all_keys if k not in seen
        ]

    result_lines: list[str] = []
    non_pair_lines = [line for key, line in meta if key is None]
    # Prepend comments/blanks that appeared before first pair
    first_pair_idx = next((i for i, (k, _) in enumerate(meta) if k is not None), len(meta))
    for _, line in meta[:first_pair_idx]:
        result_lines.append(line)

    for key in ordered_keys:
        result_lines.append(pairs[key])

    return "\n".join(result_lines)


def reorder_version(vault_dir: str, version: int, password: str,
                    key_order: list[str], alphabetical: bool = False) -> int:
    """Decrypt a version, reorder its keys, encrypt and store as new version."""
    plaintext = decrypt_file(vault_dir, version, password)
    reordered = reorder_env(plaintext.decode(), key_order, alphabetical)
    new_version = add_version(vault_dir, reordered.encode(), password)
    return new_version


def reorder_latest(vault_dir: str, password: str,
                   key_order: list[str], alphabetical: bool = False) -> int:
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        raise ValueError("No versions in vault.")
    latest = versions[-1]["version"]
    return reorder_version(vault_dir, latest, password, key_order, alphabetical)
