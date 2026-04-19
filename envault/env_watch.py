"""Watch a .env file for changes and auto-push to the vault."""
import hashlib
import time
from pathlib import Path
from typing import Callable, Optional


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def watch_file(
    env_path: Path,
    on_change: Callable[[Path], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll env_path every `interval` seconds; call on_change when it changes."""
    if not env_path.exists():
        raise FileNotFoundError(f"File not found: {env_path}")

    last_hash = _file_hash(env_path)
    iterations = 0

    while True:
        time.sleep(interval)
        iterations += 1

        if not env_path.exists():
            break

        current_hash = _file_hash(env_path)
        if current_hash != last_hash:
            last_hash = current_hash
            on_change(env_path)

        if max_iterations is not None and iterations >= max_iterations:
            break


def make_auto_push_handler(vault_dir: Path, password: str) -> Callable[[Path], None]:
    """Return a handler that pushes the changed file into the vault."""
    from envault.vault import add_version
    from envault.audit import log_event

    def handler(path: Path) -> None:
        content = path.read_bytes()
        version = add_version(vault_dir, content, password)
        log_event(vault_dir, "watch_push", {"file": str(path), "version": version})
        print(f"[envault] change detected — pushed version {version}")

    return handler
