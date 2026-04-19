"""Access control: restrict which keys a given user/role can read."""
import json
from pathlib import Path


def _access_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault" / "access.json"


def load_access(vault_dir: str) -> dict:
    p = _access_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_access(vault_dir: str, data: dict) -> None:
    p = _access_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def grant(vault_dir: str, role: str, key: str) -> None:
    """Grant role access to a specific env key."""
    data = load_access(vault_dir)
    data.setdefault(role, [])
    if key not in data[role]:
        data[role].append(key)
    save_access(vault_dir, data)


def revoke(vault_dir: str, role: str, key: str) -> None:
    """Revoke role access to a specific env key."""
    data = load_access(vault_dir)
    if role in data and key in data[role]:
        data[role].remove(key)
        if not data[role]:
            del data[role]
    save_access(vault_dir, data)


def list_grants(vault_dir: str, role: str) -> list:
    data = load_access(vault_dir)
    return data.get(role, [])


def can_access(vault_dir: str, role: str, key: str) -> bool:
    data = load_access(vault_dir)
    allowed = data.get(role, [])
    return key in allowed


def filter_env(vault_dir: str, role: str, env: dict) -> dict:
    """Return only the keys the role is allowed to see."""
    allowed = set(list_grants(vault_dir, role))
    if not allowed:
        return {}
    return {k: v for k, v in env.items() if k in allowed}
