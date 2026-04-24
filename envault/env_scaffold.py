"""Generate scaffold .env files from a list of required keys or a template."""
from __future__ import annotations

from pathlib import Path
from typing import Optional


class ScaffoldError(Exception):
    pass


def scaffold_from_keys(keys: list[str], default_value: str = "") -> str:
    """Generate a .env file string from a list of key names."""
    if not keys:
        return ""
    lines = []
    for key in keys:
        key = key.strip()
        if not key:
            continue
        if not key.replace("_", "").isalnum():
            raise ScaffoldError(f"Invalid key name: {key!r}")
        lines.append(f"{key.upper()}={default_value}")
    return "\n".join(lines) + "\n"


def scaffold_from_template(template_text: str) -> str:
    """Generate a .env scaffold from a template file.

    Template lines may be:
      KEY=<placeholder>   → kept as-is
      # comment           → kept as-is
      blank               → kept as-is
    """
    output_lines = []
    for line in template_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            output_lines.append(line)
        elif "=" in stripped:
            output_lines.append(line)
        else:
            raise ScaffoldError(f"Unrecognised template line: {line!r}")
    return "\n".join(output_lines) + "\n"


def scaffold_to_file(content: str, dest: Path, overwrite: bool = False) -> Path:
    """Write scaffold content to *dest*; raise if it exists and overwrite=False."""
    dest = Path(dest)
    if dest.exists() and not overwrite:
        raise ScaffoldError(f"{dest} already exists. Use overwrite=True to replace it.")
    dest.write_text(content, encoding="utf-8")
    return dest
