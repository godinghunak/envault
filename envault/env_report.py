"""Generate a human-readable health/status report for the vault."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import load_manifest
from envault.env_summary import summarize
from envault.env_health import run_health_check
from envault.audit import read_events
from envault.tags import load_tags


@dataclass
class ReportSection:
    title: str
    lines: List[str] = field(default_factory=list)

    def add(self, line: str) -> None:
        self.lines.append(line)

    def render(self) -> str:
        header = f"=== {self.title} ==="
        return "\n".join([header] + self.lines)


@dataclass
class VaultReport:
    sections: List[ReportSection] = field(default_factory=list)

    def add_section(self, section: ReportSection) -> None:
        self.sections.append(section)

    def render(self) -> str:
        return "\n\n".join(s.render() for s in self.sections)


def build_report(vault_dir: str, password: str, limit: int = 5) -> VaultReport:
    report = VaultReport()

    # Summary section
    summary = summarize(vault_dir, password)
    sec = ReportSection("Summary")
    sec.add(f"Total versions : {summary.total_versions}")
    sec.add(f"Latest version : {summary.latest_version or 'none'}")
    sec.add(f"Total keys     : {summary.total_keys}")
    sec.add(f"Unique keys    : {summary.unique_keys}")
    report.add_section(sec)

    # Tags section
    tags = load_tags(vault_dir)
    tsec = ReportSection("Tags")
    if tags:
        for name, version in sorted(tags.items()):
            tsec.add(f"  {name} -> v{version}")
    else:
        tsec.add("  (none)")
    report.add_section(tsec)

    # Health section
    health = run_health_check(vault_dir, password)
    hsec = ReportSection("Health")
    hsec.add(f"  Status: {'OK' if health.ok else 'ISSUES FOUND'}")
    for issue in health.issues:
        hsec.add(f"  [!] {issue}")
    if health.ok:
        hsec.add("  No issues detected.")
    report.add_section(hsec)

    # Recent activity section
    events = read_events(vault_dir)
    asec = ReportSection("Recent Activity")
    recent = events[-limit:] if len(events) >= limit else events
    if recent:
        for ev in reversed(recent):
            asec.add(f"  [{ev.get('timestamp', '?')}] {ev.get('action', '?')}: {ev.get('details', '')}")
    else:
        asec.add("  (no events logged)")
    report.add_section(asec)

    return report
