"""Sort .env file keys alphabetically or by a custom order."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple


def parse_env_lines(text: str) -> List[Tuple[str, str]]:
    """Return list of (key, raw_line) tuples, preserving comments and blanks."""
    result = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.append(("", line))
        elif "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            result.append((key, line))
        else:
            result.append(("", line))
    return result


def sort_env(
    text: str,
    *,
    reverse: bool = False,
    custom_order: Optional[List[str]] = None,
) -> str:
    """Return env text with key=value pairs sorted.

    Comments and blank lines that precede a key are kept attached to it.
    Loose leading comments/blanks are preserved at the top.

    Args:
        text: Raw .env file content.
        reverse: If True, sort descending.
        custom_order: If provided, keys appear in this order first;
                      remaining keys are sorted alphabetically after.
    """
    lines = text.splitlines()
    # Group: list of (key_or_none, [lines])
    groups: List[Tuple[Optional[str], List[str]]] = []
    pending_meta: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            pending_meta.append(line)
        elif "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            groups.append((key, pending_meta + [line]))
            pending_meta = []
        else:
            pending_meta.append(line)

    # Separate leading meta (before first key) from attached meta
    leading_meta: List[str] = []
    kv_groups: List[Tuple[str, List[str]]] = []

    for key, grp_lines in groups:
        if key is None:
            leading_meta.extend(grp_lines)
        else:
            kv_groups.append((key, grp_lines))

    if custom_order:
        order_index = {k: i for i, k in enumerate(custom_order)}
        def sort_key(item: Tuple[str, List[str]]) -> Tuple[int, str]:
            k = item[0]
            return (order_index.get(k, len(custom_order)), k)
        kv_groups.sort(key=sort_key, reverse=False)
    else:
        kv_groups.sort(key=lambda x: x[0], reverse=reverse)

    result_lines = leading_meta[:]
    if pending_meta:
        result_lines.extend(pending_meta)
    for _, grp_lines in kv_groups:
        result_lines.extend(grp_lines)

    return "\n".join(result_lines)


def sort_dict(env: Dict[str, str], *, reverse: bool = False) -> Dict[str, str]:
    """Return a new dict with keys sorted alphabetically."""
    return dict(sorted(env.items(), key=lambda x: x[0], reverse=reverse))
