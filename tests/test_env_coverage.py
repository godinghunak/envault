"""Tests for envault.env_coverage."""
from __future__ import annotations

import os
import pytest

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_coverage import (
    compute_coverage,
    format_coverage,
    KeyCoverage,
    CoverageReport,
)

PASSWORD = "testpass"


@pytest.fixture()
def vault_dir(tmp_path):
    vd = str(tmp_path / ".envault")
    init_vault(vd)
    return vd


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("KEY_A=1\nKEY_B=2\n")
    return str(p)


def push(vault_dir, env_file, content: str):
    import argparse
    env_path = env_file
    with open(env_path, "w") as f:
        f.write(content)
    args = argparse.Namespace(
        vault_dir=vault_dir, env_file=env_path, password=PASSWORD
    )
    cmd_push(args)


def test_coverage_empty_vault(vault_dir):
    report = compute_coverage(vault_dir, PASSWORD)
    assert report.versions == []
    assert report.entries == {}


def test_coverage_single_version(vault_dir, env_file):
    push(vault_dir, env_file, "ALPHA=1\nBETA=2\n")
    report = compute_coverage(vault_dir, PASSWORD)
    assert 1 in report.versions
    assert "ALPHA" in report.entries
    assert "BETA" in report.entries
    assert report.entries["ALPHA"].coverage_pct == 100.0
    assert report.entries["BETA"].present_in == [1]
    assert report.entries["BETA"].absent_from == []


def test_coverage_key_present_in_all_versions(vault_dir, env_file):
    push(vault_dir, env_file, "SHARED=x\n")
    push(vault_dir, env_file, "SHARED=y\n")
    report = compute_coverage(vault_dir, PASSWORD)
    assert report.entries["SHARED"].coverage_pct == 100.0
    assert report.entries["SHARED"].absent_from == []
    assert "SHARED" in report.full_coverage_keys


def test_coverage_key_absent_from_some_versions(vault_dir, env_file):
    push(vault_dir, env_file, "ONLY_V1=1\nCOMMON=x\n")
    push(vault_dir, env_file, "COMMON=x\n")
    report = compute_coverage(vault_dir, PASSWORD)
    assert "ONLY_V1" in report.partial_coverage_keys
    entry = report.entries["ONLY_V1"]
    assert entry.present_in == [1]
    assert entry.absent_from == [2]
    assert entry.coverage_pct == 50.0


def test_full_coverage_keys_excludes_partial(vault_dir, env_file):
    push(vault_dir, env_file, "FULL=1\nPARTIAL=x\n")
    push(vault_dir, env_file, "FULL=2\n")
    report = compute_coverage(vault_dir, PASSWORD)
    assert "FULL" in report.full_coverage_keys
    assert "PARTIAL" not in report.full_coverage_keys
    assert "PARTIAL" in report.partial_coverage_keys


def test_format_coverage_empty_vault(vault_dir):
    report = compute_coverage(vault_dir, PASSWORD)
    out = format_coverage(report)
    assert "No keys" in out


def test_format_coverage_shows_keys(vault_dir, env_file):
    push(vault_dir, env_file, "FOO=bar\n")
    report = compute_coverage(vault_dir, PASSWORD)
    out = format_coverage(report)
    assert "FOO" in out
    assert "100" in out


def test_key_coverage_str():
    kc = KeyCoverage(key="MY_KEY", present_in=[1, 2], absent_from=[3])
    assert "MY_KEY" in str(kc)
    assert "67" in str(kc) or "66" in str(kc)  # 2/3 ≈ 66.7%
