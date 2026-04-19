"""Tokenize .env values into typed tokens for analysis."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
import re

TOKEN_TYPES = {
    "url": re.compile(r"https?://[^\s]+"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "integer": re.compile(r"^-?\d+$"),
    "float": re.compile(r"^-?\d+\.\d+$"),
    "boolean": re.compile(r"^(true|false|yes|no|1|0)$", re.IGNORECASE),
    "base64": re.compile(r"^[A-Za-z0-9+/]{16,}={0,2}$"),
    "hex": re.compile(r"^[0-9a-fA-F]{8,}$"),
    "email": re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$"),
    "path": re.compile(r"^(/[^/\0]+)+/?$"),
    "string": re.compile(r".*"),
}


@dataclass
class Token:
    key: str
    value: str
    token_type: str

    def __str__(self) -> str:
        return f"{self.key}={self.value!r} [{self.token_type}]"


def detect_type(value: str) -> str:
    """Return the most specific token type for a value."""
    for name, pattern in TOKEN_TYPES.items():
        if name == "string":
            continue
        if pattern.fullmatch(value) or (name == "url" and pattern.match(value)):
            return name
    return "string"


def tokenize_env(text: str) -> List[Token]:
    """Parse env text and return a list of typed Tokens."""
    tokens: List[Token] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        tokens.append(Token(key=key, value=value, token_type=detect_type(value)))
    return tokens


def tokenize_dict(env: Dict[str, str]) -> List[Token]:
    """Tokenize a dict of key/value pairs."""
    return [Token(key=k, value=v, token_type=detect_type(v)) for k, v in env.items()]


def group_by_type(tokens: List[Token]) -> Dict[str, List[Token]]:
    """Group tokens by their detected type."""
    groups: Dict[str, List[Token]] = {}
    for token in tokens:
        groups.setdefault(token.token_type, []).append(token)
    return groups
