"""Detect and remove duplicate keys in .env content."""
from typing import List, Tuple, Dict


class DuplicateKey:
    def __init__(self, key: str, line_numbers: List[int], values: List[str]):
        self.key = key
        self.line_numbers = line_numbers
        self.values = values

    def __str__(self) -> str:
        lns = ", ".join(str(n) for n in self.line_numbers)
        return f"{self.key} (lines {lns})"


def find_duplicates(text: str) -> List[DuplicateKey]:
    """Return a list of DuplicateKey for any key appearing more than once."""
    seen: Dict[str, Tuple[List[int], List[str]]] = {}
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        if not key:
            continue
        if key not in seen:
            seen[key] = ([lineno], [value.strip()])
        else:
            seen[key][0].append(lineno)
            seen[key][1].append(value.strip())

    return [
        DuplicateKey(key, lns, vals)
        for key, (lns, vals) in seen.items()
        if len(lns) > 1
    ]


def dedupe_env(text: str, keep: str = "last") -> str:
    """Remove duplicate keys, keeping either the 'first' or 'last' occurrence."""
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    lines = text.splitlines(keepends=True)
    key_positions: Dict[str, List[int]] = {}

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key = stripped.partition("=")[0].strip()
        if key:
            key_positions.setdefault(key, []).append(idx)

    skip: set = set()
    for key, positions in key_positions.items():
        if len(positions) > 1:
            to_remove = positions[1:] if keep == "first" else positions[:-1]
            skip.update(to_remove)

    return "".join(line for idx, line in enumerate(lines) if idx not in skip)


def dedupe_dict(d: Dict[str, str]) -> Dict[str, str]:
    """Dicts are already deduplicated by nature; return a copy."""
    return dict(d)


def summarize_duplicates(text: str) -> str:
    """Return a human-readable summary of duplicate keys found in *text*.

    Returns an empty string if no duplicates are detected.
    """
    duplicates = find_duplicates(text)
    if not duplicates:
        return ""
    lines = [f"Found {len(duplicates)} duplicate key(s):"]
    for dup in duplicates:
        values_str = ", ".join(f'"{v}"' for v in dup.values)
        lines.append(f"  {dup.key}: lines {', '.join(str(n) for n in dup.line_numbers)} -> values {values_str}")
    return "\n".join(lines)
