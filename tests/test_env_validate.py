"""Tests for envault.env_validate."""

from __future__ import annotations

import pytest

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_validate import validate_version, validate_file, ValidationReport


@pytest.fixture()
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    init_vault(str(d))
    return str(d)


@pytest.fixture()
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_SECRET=hunter2\n")
    return str(f)


@pytest.fixture()
def schema_file(tmp_path):
    s = tmp_path / "schema.envschema"
    s.write_text("DB_HOST required\nDB_PORT required\nAPP_SECRET required\n")
    return str(s)


def push(vault_dir, env_file, password="pass"):
    import argparse
    args = argparse.Namespace(
        vault_dir=vault_dir, env_file=env_file, password=password
    )
    cmd_push(args)


def test_validate_version_ok(vault_dir, env_file, schema_file):
    push(vault_dir, env_file)
    report = validate_version(vault_dir, "pass", schema_file)
    assert isinstance(report, ValidationReport)
    assert report.ok is True
    assert report.violations == []


def test_validate_version_missing_key(vault_dir, tmp_path, schema_file):
    env = tmp_path / ".env2"
    env.write_text("DB_HOST=localhost\n")
    push(vault_dir, str(env))
    report = validate_version(vault_dir, "pass", schema_file)
    assert report.ok is False
    assert any("DB_PORT" in str(v) for v in report.violations)


def test_validate_version_specific_version(vault_dir, env_file, schema_file):
    push(vault_dir, env_file)
    report = validate_version(vault_dir, "pass", schema_file, version=1)
    assert report.version == 1
    assert report.ok is True


def test_validate_version_empty_vault_raises(vault_dir, schema_file):
    with pytest.raises(ValueError, match="No versions"):
        validate_version(vault_dir, "pass", schema_file)


def test_validate_file_ok(env_file, schema_file):
    report = validate_file(env_file, schema_file)
    assert report.ok is True


def test_validate_file_missing_key(tmp_path, schema_file):
    f = tmp_path / "partial.env"
    f.write_text("DB_HOST=localhost\n")
    report = validate_file(str(f), schema_file)
    assert report.ok is False


def test_validate_file_ignores_comments(tmp_path, schema_file):
    f = tmp_path / ".env"
    f.write_text("# comment\nDB_HOST=x\nDB_PORT=1\nAPP_SECRET=s\n")
    report = validate_file(str(f), schema_file)
    assert report.ok is True


def test_validation_report_repr(vault_dir, env_file, schema_file):
    push(vault_dir, env_file)
    report = validate_version(vault_dir, "pass", schema_file)
    assert "ValidationReport" in repr(report)
