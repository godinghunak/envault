"""Tests for envault.env_report."""

from __future__ import annotations

import os
import pytest

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_report import build_report, ReportSection, VaultReport


PASSWORD = "reportpass"


@pytest.fixture()
def vault_dir(tmp_path):
    d = str(tmp_path / ".envault")
    init_vault(d)
    return d


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n")
    return str(p)


def push(vault_dir, env_file):
    import argparse
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=PASSWORD)
    cmd_push(args)


# --- ReportSection ---

def test_report_section_render_contains_title():
    sec = ReportSection("Overview")
    sec.add("line one")
    rendered = sec.render()
    assert "=== Overview ===" in rendered
    assert "line one" in rendered


def test_report_section_empty_lines():
    sec = ReportSection("Empty")
    rendered = sec.render()
    assert "=== Empty ===" in rendered


# --- VaultReport ---

def test_vault_report_render_joins_sections():
    r = VaultReport()
    s1 = ReportSection("A")
    s1.add("alpha")
    s2 = ReportSection("B")
    s2.add("beta")
    r.add_section(s1)
    r.add_section(s2)
    rendered = r.render()
    assert "=== A ==" in rendered
    assert "=== B ==" in rendered
    assert "alpha" in rendered
    assert "beta" in rendered


# --- build_report ---

def test_build_report_empty_vault(vault_dir):
    report = build_report(vault_dir, PASSWORD)
    rendered = report.render()
    assert "Summary" in rendered
    assert "Health" in rendered
    assert "Tags" in rendered
    assert "Recent Activity" in rendered


def test_build_report_after_push(vault_dir, env_file):
    push(vault_dir, env_file)
    report = build_report(vault_dir, PASSWORD)
    rendered = report.render()
    assert "Total versions" in rendered
    assert "Latest version" in rendered


def test_build_report_shows_no_events_before_any(vault_dir):
    report = build_report(vault_dir, PASSWORD)
    rendered = report.render()
    assert "no events logged" in rendered


def test_build_report_limit_parameter(vault_dir, env_file):
    for _ in range(3):
        push(vault_dir, env_file)
    report = build_report(vault_dir, PASSWORD, limit=2)
    rendered = report.render()
    assert "Recent Activity" in rendered
