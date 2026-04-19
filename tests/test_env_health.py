"""Tests for envault.env_health module."""

import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_health import run_health_check, HealthReport
from envault.env_expire import load_expiry, save_expiry
from envault.env_quota import load_quota, save_quota
import argparse


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\nSECRET=abc123\n")
    return str(f)


def push(vault_dir, env_file, password="pass"):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def test_health_check_empty_vault(vault_dir):
    report = run_health_check(vault_dir)
    assert isinstance(report, HealthReport)
    messages = [i.message for i in report.issues]
    assert any("No versions" in m for m in messages)


def test_health_check_ok_is_true_with_no_errors(vault_dir):
    report = run_health_check(vault_dir)
    assert report.ok is True


def test_health_check_uninitialized_vault(tmp_path):
    report = run_health_check(str(tmp_path))
    assert not report.ok
    assert any(i.severity == "error" for i in report.issues)


def test_health_check_after_push(vault_dir, env_file):
    push(vault_dir, env_file)
    report = run_health_check(vault_dir)
    assert report.ok
    messages = [i.message for i in report.issues]
    assert any("1 version" in m for m in messages)


def test_health_check_expired_version(vault_dir, env_file):
    push(vault_dir, env_file)
    expiry = load_expiry(vault_dir)
    expiry["1"] = "2000-01-01T00:00:00"
    save_expiry(vault_dir, expiry)
    report = run_health_check(vault_dir)
    warnings = [i for i in report.issues if i.severity == "warning"]
    assert any("expired" in w.message for w in warnings)


def test_health_check_quota_exceeded(vault_dir, env_file):
    push(vault_dir, env_file)
    quota = load_quota(vault_dir)
    quota["max_versions"] = 1
    save_quota(vault_dir, quota)
    report = run_health_check(vault_dir)
    warnings = [i for i in report.issues if i.severity == "warning"]
    assert any("quota" in w.message.lower() for w in warnings)
