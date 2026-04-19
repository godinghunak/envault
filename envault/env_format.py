"""Format/normalize .env file contents."""
from __future__ import annotations

from typing import List, Tuple


def parse_lines(text: str) -> List[Tuple[str, str, str]]:
    """Return list of (kind, key, raw_line) where kind is 'pair'|'comment'|'blank'."""
    result = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            result.append(("blank", "", line))
        elif stripped.startswith("#"):
            result.append(("comment", "", line))
        elif "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            result.append(("pair", key, line))
        else:
            result.append(("pair", "", line))
    return result


def format_env(
    text: str,
    *,
    sort_keys: bool = False,
    strip_quotes: bool = False,
    uppercase_keys: bool = False,
    remove_blanks: bool = False,
) -> str:
    """Return a normalised version of the env text."""
    lines_out: List[str] = []
    pairs: List[Tuple[str, str]] = []  # (key, formatted_line)
    others: List[Tuple[int, str]] = []  # (original_index, line)

    parsed = parse_lines(text)

    for idx, (kind, key, raw) in enumerate(parsed):
        if kind == "blank":
            if not remove_blanks:
                others.append((idx, ""))
        elif kind == "comment":
            others.append((idx, raw))
        else:
            if "=" in raw:
                k, v = raw.split("=", 1)
                k = k.strip()
                v = v.strip()
                if uppercase_keys:
                    k = k.upper()
                if strip_quotes and len(v) >= 2 and v[0] in ('"', "'") and v[-1] == v[0]:
                    v = v[1:-1]
                pairs.append((k, f"{k}={v}"))
            else:
                others.append((idx, raw))

    if sort_keys:
        pairs.sort(key=lambda x: x[0].lower())

    if sort_keys:
        # sorted output: comments/blanks first, then sorted pairs
        for _, line in others:
            lines_out.append(line)
        for _, line in pairs:
            lines_out.append(line)
    else:
        # rebuild in original order, replacing pair lines in-order
        pair_iter = iter(pairs)
        for idx, (kind, key, raw) in enumerate(parsed):
            if kind == "blank":
                if not remove_blanks:
                    lines_out.append("")
            elif kind == "comment":
                lines_out.append(raw)
            else:
                if "=" in raw:
                    _, line = next(pair_iter)
                    lines_out.append(line)
                else:
                    lines_out.append(raw)

    return "\n".join(lines_out)
