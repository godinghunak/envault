"""Health check module for envault vaults."""

from dataclasses import dataclass, field
from typing import List
from envault.vault import load_manifest, _vault_path
from envault.env_expire import load_expiry, is_expired
from envault.env_lock import read_lock, verify_lock
from envault.env_quota import load_quota, get_quota, current_version_count
import os


@dataclass
class HealthIssue:
    severity: str  # 'error' | 'warning' | 'info'
    message: str

    def __str__(self):
        return f"[{self.severity.upper()}] {self.message}"


@dataclass
class HealthReport:
    issues: List[HealthIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    def add(self, severity: str, message: str):
        self.issues.append(HealthIssue(severity, message))


def check_vault_initialized(vault_dir: str, report: HealthReport):
    path = _vault_path(vault_dir)
    if not os.path.isdir(path):
        report.add("error", "Vault directory does not exist. Run 'envault init'.")
        return False
    return True


def check_versions(vault_dir: str, report: HealthReport):
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        report.add("info", "No versions pushed yet.")
    else:
        report.add("info", f"{len(versions)} version(s) found.")


def check_expiry(vault_dir: str, report: HealthReport):
    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    expiry = load_expiry(vault_dir)
    for v in versions:
        if is_expired(expiry, v):
            report.add("warning", f"Version {v} has expired.")


def check_quota(vault_dir: str, report: HealthReport):
    quota = load_quota(vault_dir)
    limit = get_quota(quota)
    count = current_version_count(vault_dir)
    if limit and count >= limit:
        report.add("warning", f"Version quota reached ({count}/{limit}).")


def check_lock(vault_dir: str, report: HealthReport):
    try:
        lock = read_lock(vault_dir)
        if lock:
            ok, msg = verify_lock(vault_dir, lock["version"])
            if not ok:
                report.add("error", f"Lock file mismatch: {msg}")
            else:
                report.add("info", "Lock file verified OK.")
    except FileNotFoundError:
        report.add("info", "No lock file present.")
    except Exception as e:
        report.add("warning", f"Could not verify lock: {e}")


def run_health_check(vault_dir: str) -> HealthReport:
    report = HealthReport()
    if not check_vault_initialized(vault_dir, report):
        return report
    check_versions(vault_dir, report)
    check_expiry(vault_dir, report)
    check_quota(vault_dir, report)
    check_lock(vault_dir, report)
    return report
