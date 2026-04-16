"""CLI commands for audit log inspection."""
import json
from envault.audit import read_events, clear_log


def cmd_log(args) -> None:
    """Print audit log events."""
    vault_dir = getattr(args, "vault_dir", ".")
    events = read_events(vault_dir)
    if not events:
        print("No audit events found.")
        return
    limit = getattr(args, "limit", None)
    if limit:
        events = events[-limit:]
    for event in events:
        ts = event.get("timestamp", "?")
        action = event.get("action", "?")
        details = {k: v for k, v in event.items() if k not in ("timestamp", "action")}
        detail_str = " ".join(f"{k}={v}" for k, v in details.items())
        print(f"[{ts}] {action.upper():<10} {detail_str}")


def cmd_log_clear(args) -> None:
    """Clear the audit log."""
    vault_dir = getattr(args, "vault_dir", ".")
    clear_log(vault_dir)
    print("Audit log cleared.")
