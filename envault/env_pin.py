"""Pin a specific vault version as the 'stable' reference."""

import json
from pathlib import Path
from envault.vault import _vault_path, load_manifest


def _pin_path(vault_dir: str) -> Path:
    return _vault_path(vault_dir) / "pin.json"


def load_pin(vault_dir: str) -> dict:
    p = _pin_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_pin(vault_dir: str, data: dict) -> None:
    _pin_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_pin(vault_dir: str, version: int, label: str = "stable") -> None:
    manifest = load_manifest(vault_dir)
    versions = [e["version"] for e in manifest.get("versions", [])]
    if version not in versions:
        raise ValueError(f"Version {version} does not exist in vault.")
    data = load_pin(vault_dir)
    data[label] = version
    save_pin(vault_dir, data)


def get_pin(vault_dir: str, label: str = "stable") -> int | None:
    data = load_pin(vault_dir)
    return data.get(label)


def remove_pin(vault_dir: str, label: str = "stable") -> bool:
    data = load_pin(vault_dir)
    if label not in data:
        return False
    del data[label]
    save_pin(vault_dir, data)
    return True


def list_pins(vault_dir: str) -> dict:
    return load_pin(vault_dir)
