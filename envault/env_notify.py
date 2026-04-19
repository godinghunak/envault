"""Notification hooks for vault events."""
import json
import urllib.request
import urllib.error
from pathlib import Path


def _notify_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault" / "notify.json"


def load_notify_config(vault_dir: str) -> dict:
    p = _notify_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_notify_config(vault_dir: str, config: dict) -> None:
    p = _notify_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(config, indent=2))


def set_webhook(vault_dir: str, url: str) -> None:
    config = load_notify_config(vault_dir)
    config["webhook_url"] = url
    save_notify_config(vault_dir, config)


def remove_webhook(vault_dir: str) -> None:
    config = load_notify_config(vault_dir)
    config.pop("webhook_url", None)
    save_notify_config(vault_dir, config)


def get_webhook(vault_dir: str) -> str | None:
    return load_notify_config(vault_dir).get("webhook_url")


def send_notification(vault_dir: str, event: str, details: dict) -> bool:
    """Send a webhook notification. Returns True on success."""
    url = get_webhook(vault_dir)
    if not url:
        return False
    payload = json.dumps({"event": event, "details": details}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5):
            return True
    except (urllib.error.URLError, OSError):
        return False
