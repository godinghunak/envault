"""Pre/post push hooks support for envault."""
import os
import subprocess
from pathlib import Path

HOOK_PRE_PUSH = "pre-push"
HOOK_POST_PUSH = "post-push"


def _hooks_dir(vault_dir: str) -> Path:
    return Path(vault_dir) / "hooks"


def init_hooks(vault_dir: str) -> None:
    """Create the hooks directory if it doesn't exist."""
    _hooks_dir(vault_dir).mkdir(parents=True, exist_ok=True)


def hook_path(vault_dir: str, hook_name: str) -> Path:
    return _hooks_dir(vault_dir) / hook_name


def install_hook(vault_dir: str, hook_name: str, script: str) -> None:
    """Write a hook script and make it executable."""
    if hook_name not in (HOOK_PRE_PUSH, HOOK_POST_PUSH):
        raise ValueError(f"Unknown hook: {hook_name}")
    path = hook_path(vault_dir, hook_name)
    path.write_text(script)
    path.chmod(0o755)


def remove_hook(vault_dir: str, hook_name: str) -> bool:
    """Remove a hook. Returns True if it existed."""
    path = hook_path(vault_dir, hook_name)
    if path.exists():
        path.unlink()
        return True
    return False


def run_hook(vault_dir: str, hook_name: str, env: dict = None) -> int:
    """Run a hook script if it exists. Returns exit code (0 if no hook)."""
    path = hook_path(vault_dir, hook_name)
    if not path.exists():
        return 0
    merged_env = {**os.environ, **(env or {})}
    result = subprocess.run([str(path)], env=merged_env)
    return result.returncode


def list_hooks(vault_dir: str) -> list:
    """Return names of installed hooks."""
    d = _hooks_dir(vault_dir)
    if not d.exists():
        return []
    return [p.name for p in d.iterdir() if p.is_file()]
