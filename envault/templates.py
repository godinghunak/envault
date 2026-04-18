"""Template support: save/load named .env templates stripped of values."""
import json
from pathlib import Path


def _templates_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "templates.json"


def load_templates(vault_dir: str) -> dict:
    p = _templates_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_templates(vault_dir: str, templates: dict) -> None:
    _templates_path(vault_dir).write_text(json.dumps(templates, indent=2))


def add_template(vault_dir: str, name: str, keys: list[str]) -> None:
    """Store a template as an ordered list of keys (no values)."""
    templates = load_templates(vault_dir)
    templates[name] = keys
    save_templates(vault_dir, templates)


def remove_template(vault_dir: str, name: str) -> None:
    templates = load_templates(vault_dir)
    if name not in templates:
        raise KeyError(f"Template '{name}' not found.")
    del templates[name]
    save_templates(vault_dir, templates)


def get_template(vault_dir: str, name: str) -> list[str]:
    templates = load_templates(vault_dir)
    if name not in templates:
        raise KeyError(f"Template '{name}' not found.")
    return templates[name]


def list_templates(vault_dir: str) -> list[str]:
    return list(load_templates(vault_dir).keys())


def template_from_env_content(content: str) -> list[str]:
    """Parse env file content and return list of keys (ignoring comments/blanks)."""
    keys = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key = line.split("=", 1)[0].strip()
            keys.append(key)
    return keys


def render_template(keys: list[str]) -> str:
    """Render a template as an env file with empty values."""
    return "\n".join(f"{k}=" for k in keys) + "\n"
