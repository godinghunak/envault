"""Schema validation for .env files — check required keys, types, and patterns."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Sch:
    key: str
    required: bool = True
    pattern: Optional[str] = None
    description: str = ""


@dataclass
class SchemaViolation:
    key: str
    message: str

    def __str__(self) -> str:
        return f"{self.key}: {self.message}"


def load_text: str) -> list[SchemaRule]:
    """Parse a simple schema format: each line is KEY [required|optional] [/pattern/] [# desc]"""
    rules = []
    for line in schema_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        desc = ""
        if "#" in line:
            line, desc = line.split("#", 1)
            desc = desc.strip()
        parts = line.split()
        if not parts:
            continue
        key = parts[0]
        required = True
        pattern = None
        for part in parts[1:]:
            if part.lower() == "optional":
                required = False
            elif part.lower() == "required":
                required = True
            elif part.startswith("/") and part.endswith("/"):
                pattern = part[1:-1]
        rules.append(SchemaRule(key=key, required=required, pattern=pattern, description=desc))
    return rules


def validate_env(env: dict[str, str], rules: list[SchemaRule]) -> list[SchemaViolation]:
    """Validate an env dict against schema rules, returning a list of violations."""
    violations = []
    for rule in rules:
        if rule.key not in env:
            if rule.required:
                violations.append(SchemaViolation(rule.key, "required key is missing"))
            continue
        value = env[rule.key]
        if rule.pattern:
            if not re.fullmatch(rule.pattern, value):
                violations.append(
                    SchemaViolation(rule.key, f"value {value!r} does not match pattern /{rule.pattern}/")
                )
    return violations


def validate_env_text(env_text: str, schema_text: str) -> list[SchemaViolation]:
    """Convenience: parse env text and validate against schema text."""
    from envault.diff import parse_env
    env = parse_env(env_text)
    rules = load_schema(schema_text)
    return validate_env(env, rules)
