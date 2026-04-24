"""Classify .env keys by category based on naming conventions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Category patterns: (category_name, compiled_regex)
_CATEGORY_PATTERNS: List[tuple] = [
    ("database", re.compile(r"(DB|DATABASE|POSTGRES|MYSQL|MONGO|REDIS|SQLITE)", re.I)),
    ("auth",     re.compile(r"(AUTH|JWT|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL)", re.I)),
    ("api",      re.compile(r"(API|ENDPOINT|URL|URI|HOST|PORT|BASEURL|BASE_URL)", re.I)),
    ("cloud",    re.compile(r"(AWS|GCP|AZURE|S3|BUCKET|REGION|CLOUD)", re.I)),
    ("email",    re.compile(r"(MAIL|EMAIL|SMTP|SENDGRID|MAILGUN)", re.I)),
    ("logging",  re.compile(r"(LOG|LOGGING|SENTRY|DATADOG|NEWRELIC|DEBUG)", re.I)),
    ("feature",  re.compile(r"(FEATURE|FLAG|FF_|TOGGLE)", re.I)),
]

_OTHER = "other"


@dataclass
class ClassifiedKey:
    key: str
    value: str
    category: str

    def __str__(self) -> str:
        return f"[{self.category}] {self.key}={self.value}"


@dataclass
class ClassifyResult:
    categories: Dict[str, List[ClassifiedKey]] = field(default_factory=dict)

    def add(self, item: ClassifiedKey) -> None:
        self.categories.setdefault(item.category, []).append(item)

    def get(self, category: str) -> List[ClassifiedKey]:
        return self.categories.get(category, [])

    def all_categories(self) -> List[str]:
        return sorted(self.categories.keys())

    def total(self) -> int:
        return sum(len(v) for v in self.categories.values())


def classify_key(key: str) -> str:
    """Return the category name for a single key."""
    for category, pattern in _CATEGORY_PATTERNS:
        if pattern.search(key):
            return category
    return _OTHER


def classify_env(env: Dict[str, str]) -> ClassifyResult:
    """Classify all keys in an env dict and return a ClassifyResult."""
    result = ClassifyResult()
    for key, value in env.items():
        category = classify_key(key)
        result.add(ClassifiedKey(key=key, value=value, category=category))
    return result


def format_classify_result(result: ClassifyResult) -> str:
    """Format a ClassifyResult as a human-readable string."""
    if result.total() == 0:
        return "No keys to classify."
    lines: List[str] = []
    for category in result.all_categories():
        items = result.get(category)
        lines.append(f"[{category}] ({len(items)} key(s))")
        for item in items:
            lines.append(f"  {item.key}")
    return "\n".join(lines)
