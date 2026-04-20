"""Split a .env file into multiple named profiles or files by prefix or key list."""

from typing import Dict, List, Optional
from envault.diff import parse_env


class SplitResult:
    def __init__(self):
        self.parts: Dict[str, Dict[str, str]] = {}

    def add(self, name: str, data: Dict[str, str]):
        self.parts[name] = data

    def names(self) -> List[str]:
        return sorted(self.parts.keys())

    def get(self, name: str) -> Dict[str, str]:
        return self.parts.get(name, {})


def split_by_prefix(env: Dict[str, str], sep: str = "_") -> SplitResult:
    """Split env dict into groups based on key prefix before the separator."""
    result = SplitResult()
    for key, value in env.items():
        if sep in key:
            prefix = key.split(sep, 1)[0].lower()
        else:
            prefix = "other"
        if prefix not in result.parts:
            result.parts[prefix] = {}
        result.parts[prefix][key] = value
    return result


def split_by_keys(env: Dict[str, str], groups: Dict[str, List[str]]) -> SplitResult:
    """Split env dict by explicit key groupings. Unmatched keys go to 'other'."""
    result = SplitResult()
    assigned: set = set()
    for group_name, keys in groups.items():
        result.parts[group_name] = {}
        for key in keys:
            if key in env:
                result.parts[group_name][key] = env[key]
                assigned.add(key)
    leftover = {k: v for k, v in env.items() if k not in assigned}
    if leftover:
        result.parts["other"] = leftover
    return result


def split_env_text(text: str, sep: str = "_") -> SplitResult:
    """Parse env text and split by prefix."""
    env = parse_env(text)
    return split_by_prefix(env, sep)


def format_split_part(data: Dict[str, str]) -> str:
    """Format a split part back to .env text."""
    lines = [f"{k}={v}" for k, v in sorted(data.items())]
    return "\n".join(lines) + ("\n" if lines else "")
