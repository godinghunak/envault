"""Flatten nested environment variable prefixes into a single-level dict.

For example, given keys like DB__HOST, DB__PORT, APP__NAME, this module
can flatten them into a structured representation or vice-versa expand
a nested dict into flat env-style keys.
"""

from typing import Dict, Any, List


SEPARATOR = "__"


def flatten_to_dict(env: Dict[str, str], sep: str = SEPARATOR) -> Dict[str, Any]:
    """Convert flat env keys like DB__HOST into nested dicts: {DB: {HOST: ...}}."""
    result: Dict[str, Any] = {}
    for key, value in env.items():
        parts = key.split(sep)
        node = result
        for part in parts[:-1]:
            if part not in node or not isinstance(node[part], dict):
                node[part] = {}
            node = node[part]
        node[parts[-1]] = value
    return result


def expand_from_dict(nested: Dict[str, Any], sep: str = SEPARATOR, prefix: str = "") -> Dict[str, str]:
    """Convert a nested dict back into flat env-style keys."""
    result: Dict[str, str] = {}
    for key, value in nested.items():
        full_key = f"{prefix}{sep}{key}" if prefix else key
        if isinstance(value, dict):
            result.update(expand_from_dict(value, sep=sep, prefix=full_key))
        else:
            result[full_key] = str(value)
    return result


def list_prefixes(env: Dict[str, str], sep: str = SEPARATOR) -> List[str]:
    """Return all top-level prefix groups found in the env keys."""
    prefixes = set()
    for key in env:
        if sep in key:
            prefixes.add(key.split(sep)[0])
    return sorted(prefixes)


def flatten_env_text(text: str, sep: str = SEPARATOR) -> Dict[str, Any]:
    """Parse env text and return a nested dict."""
    env: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return flatten_to_dict(env, sep=sep)
