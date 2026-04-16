"""Audit log for envault operations."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

AUDIT_FILE = ".envault/audit.log"


def _audit_path(vault_dir: str = ".") -> Path:
    return Path(vault_dir) / ".envault" / "audit.log"


def log_event(action: str, details: dict, vault_dir: str = ".") -> None:
    """Append a structured audit event to the log."""
    path = _audit_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        **details,
    }
    with open(path, "a") as f:
        f.write(json.dumps(event) + "\n")


def read_events(vault_dir: str = ".") -> list[dict]:
    """Return all audit events as a list of dicts."""
    path = _audit_path(vault_dir)
    if not path.exists():
        return []
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def clear_log(vault_dir: str = ".") -> None:
    """Clear the audit log."""
    path = _audit_path(vault_dir)
    if path.exists():
        path.unlink()
