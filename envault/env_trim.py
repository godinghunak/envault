"""Trim whitespace and normalize values in .env files."""

from typing import Dict, List, Tuple


def trim_value(value: str) -> str:
    """Strip leading/trailing whitespace from a value."""
    return value.strip()


def trim_env(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new dict with all values trimmed."""
    return {k: trim_value(v) for k, v in env.items()}


def find_untrimmed(env: Dict[str, str]) -> List[Tuple[str, str, str]]:
    """Return list of (key, original, trimmed) for values that need trimming."""
    result = []
    for k, v in env.items():
        trimmed = trim_value(v)
        if trimmed != v:
            result.append((k, v, trimmed))
    return result


def trim_env_text(text: str) -> str:
    """Trim values in raw .env text, preserving comments and blank lines."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            lines.append(line)
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            lines.append(f"{key}={value.strip()}")
        else:
            lines.append(line)
    return "\n".join(lines)


def trim_version(vault_dir: str, version: int, password: str) -> str:
    """Decrypt a version, trim values, re-encrypt and push. Returns new content."""
    from envault.export import export_version
    from envault.vault import add_version
    from envault.diff import parse_env

    content = export_version(vault_dir, version, password)
    trimmed_content = trim_env_text(content)
    add_version(vault_dir, trimmed_content.encode(), password)
    return trimmed_content
