"""Detect and parse heredoc-style multiline values in .env files."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class HeredocIssue:
    line: int
    message: str

    def __str__(self) -> str:
        return f"Line {self.line}: {self.message}"


def find_heredocs(text: str) -> List[Tuple[str, str]]:
    """Return list of (key, multiline_value) pairs found via heredoc syntax.

    Supports the pattern:
        KEY=<<EOF
        line1
        line2
        EOF
    """
    results: List[Tuple[str, str]] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if "=<<" in line:
            key, _, marker = line.partition("=<<")
            key = key.strip()
            marker = marker.strip()
            if key and marker:
                body_lines: List[str] = []
                i += 1
                while i < len(lines) and lines[i].strip() != marker:
                    body_lines.append(lines[i])
                    i += 1
                results.append((key, "\n".join(body_lines)))
        i += 1
    return results


def validate_heredocs(text: str) -> List[HeredocIssue]:
    """Return issues for unclosed heredoc blocks."""
    issues: List[HeredocIssue] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if "=<<" in line:
            key, _, marker = line.partition("=<<")
            marker = marker.strip()
            start = i + 1
            i += 1
            closed = False
            while i < len(lines):
                if lines[i].strip() == marker:
                    closed = True
                    break
                i += 1
            if not closed:
                issues.append(HeredocIssue(start, f"Unclosed heredoc block (marker '{marker}' never found)"))
        i += 1
    return issues


def expand_heredocs(text: str) -> Dict[str, str]:
    """Parse all heredoc blocks and return a dict of key -> value."""
    return dict(find_heredocs(text))
