"""env_preview.py – render a decrypted version as a shell-export block or dotenv block."""
from __future__ import annotations

from typing import Dict, List, Optional

from envault.diff import parse_env
from envault.export import export_version, export_latest
from envault.vault import load_manifest


class PreviewError(Exception):
    pass


def _load_env_dict(vault_dir: str, password: str, version: Optional[int] = None) -> Dict[str, str]:
    """Decrypt a version and return its key/value pairs."""
    if version is None:
        plaintext = export_latest(vault_dir, password)
    else:
        plaintext = export_version(vault_dir, version, password)
    return parse_env(plaintext)


def preview_dotenv(vault_dir: str, password: str, version: Optional[int] = None,
                   keys: Optional[List[str]] = None) -> str:
    """Return the env as a .env-style block, optionally filtered to *keys*."""
    env = _load_env_dict(vault_dir, password, version)
    if keys:
        env = {k: v for k, v in env.items() if k in keys}
    lines = [f"{k}={v}" for k, v in sorted(env.items())]
    return "\n".join(lines)


def preview_export(vault_dir: str, password: str, version: Optional[int] = None,
                   keys: Optional[List[str]] = None) -> str:
    """Return the env as shell *export* statements."""
    env = _load_env_dict(vault_dir, password, version)
    if keys:
        env = {k: v for k, v in env.items() if k in keys}
    lines = [f"export {k}={v!r}" for k, v in sorted(env.items())]
    return "\n".join(lines)


def preview_json(vault_dir: str, password: str, version: Optional[int] = None,
                 keys: Optional[List[str]] = None) -> str:
    """Return the env as a JSON object string."""
    import json
    env = _load_env_dict(vault_dir, password, version)
    if keys:
        env = {k: v for k, v in env.items() if k in keys}
    return json.dumps(dict(sorted(env.items())), indent=2)


FORMATS = {"dotenv": preview_dotenv, "export": preview_export, "json": preview_json}


def preview(vault_dir: str, password: str, fmt: str = "dotenv",
            version: Optional[int] = None, keys: Optional[List[str]] = None) -> str:
    """Dispatch to the requested format renderer."""
    if fmt not in FORMATS:
        raise PreviewError(f"Unknown format '{fmt}'. Choose from: {', '.join(FORMATS)}")
    return FORMATS[fmt](vault_dir, password, version, keys)
