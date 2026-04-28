"""Export audit log entries to various formats (JSON, CSV, plain text)."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from envault.audit import read_events


def export_audit_json(vault_dir: str, limit: int | None = None) -> str:
    """Return audit events serialised as a JSON string."""
    events = read_events(vault_dir)
    if limit is not None:
        events = events[-limit:]
    return json.dumps(events, indent=2)


def export_audit_csv(vault_dir: str, limit: int | None = None) -> str:
    """Return audit events serialised as a CSV string."""
    events = read_events(vault_dir)
    if limit is not None:
        events = events[-limit:]

    if not events:
        return ""

    fieldnames = ["timestamp", "action", "details"]
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=fieldnames,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for event in events:
        writer.writerow(
            {
                "timestamp": event.get("timestamp", ""),
                "action": event.get("action", ""),
                "details": event.get("details", ""),
            }
        )
    return buf.getvalue()


def export_audit_text(vault_dir: str, limit: int | None = None) -> str:
    """Return audit events as a human-readable plain-text string."""
    events = read_events(vault_dir)
    if limit is not None:
        events = events[-limit:]

    if not events:
        return "No audit events found."

    lines: List[str] = []
    for event in events:
        ts = event.get("timestamp", "?")
        action = event.get("action", "?")
        details = event.get("details", "")
        line = f"[{ts}] {action}"
        if details:
            line += f" — {details}"
        lines.append(line)
    return "\n".join(lines)


SUPPORTED_FORMATS = ("json", "csv", "text")


def export_audit(
    vault_dir: str,
    fmt: str = "text",
    limit: int | None = None,
) -> str:
    """Dispatch to the correct exporter based on *fmt*."""
    fmt = fmt.lower()
    if fmt == "json":
        return export_audit_json(vault_dir, limit)
    if fmt == "csv":
        return export_audit_csv(vault_dir, limit)
    if fmt == "text":
        return export_audit_text(vault_dir, limit)
    raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}")
