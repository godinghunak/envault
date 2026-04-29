"""Watermark support: embed and verify hidden metadata in encrypted vault versions."""

import hashlib
import json
import time
from pathlib import Path

from envault.vault import _vault_path


def _watermarks_path(vault_dir: str) -> Path:
    return _vault_path(vault_dir) / "watermarks.json"


def load_watermarks(vault_dir: str) -> dict:
    p = _watermarks_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_watermarks(vault_dir: str, data: dict) -> None:
    p = _watermarks_path(vault_dir)
    p.write_text(json.dumps(data, indent=2))


def _compute_mark(version: int, author: str, secret: str) -> str:
    payload = f"{version}:{author}:{secret}"
    return hashlib.sha256(payload.encode()).hexdigest()


def stamp(vault_dir: str, version: int, author: str, secret: str, note: str = "") -> str:
    """Embed a watermark for the given version. Returns the mark hex string."""
    mark = _compute_mark(version, author, secret)
    wm = load_watermarks(vault_dir)
    wm[str(version)] = {
        "author": author,
        "note": note,
        "mark": mark,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    save_watermarks(vault_dir, wm)
    return mark


def verify(vault_dir: str, version: int, author: str, secret: str) -> bool:
    """Return True if the stored watermark matches the expected mark."""
    wm = load_watermarks(vault_dir)
    entry = wm.get(str(version))
    if entry is None:
        return False
    expected = _compute_mark(version, author, secret)
    return entry["mark"] == expected


def get_watermark(vault_dir: str, version: int) -> dict | None:
    wm = load_watermarks(vault_dir)
    return wm.get(str(version))


def list_watermarks(vault_dir: str) -> list[dict]:
    wm = load_watermarks(vault_dir)
    return [
        {"version": int(v), **info}
        for v, info in sorted(wm.items(), key=lambda x: int(x[0]))
    ]


def remove_watermark(vault_dir: str, version: int) -> bool:
    wm = load_watermarks(vault_dir)
    key = str(version)
    if key not in wm:
        return False
    del wm[key]
    save_watermarks(vault_dir, wm)
    return True
