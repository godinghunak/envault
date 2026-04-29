"""Tests for envault.env_preview."""
from __future__ import annotations

import json
import os

import pytest

from envault.commands import cmd_init, cmd_push
from envault.env_preview import preview, preview_dotenv, preview_export, preview_json, PreviewError


PASSWORD = "test-secret"


@pytest.fixture()
def vault_dir(tmp_path):
    class A:
        vault = str(tmp_path)
    cmd_init(A())
    return str(tmp_path)


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPI_KEY=abc123\n")
    return str(p)


def push(vault_dir, env_file, password=PASSWORD):
    class A:
        vault = vault_dir
        file = env_file
        pw = password
    cmd_push(A())


# ---------------------------------------------------------------------------

def test_preview_dotenv_contains_keys(vault_dir, env_file):
    push(vault_dir, env_file)
    result = preview_dotenv(vault_dir, PASSWORD)
    assert "DB_HOST=localhost" in result
    assert "DB_PORT=5432" in result
    assert "API_KEY=abc123" in result


def test_preview_dotenv_filtered_keys(vault_dir, env_file):
    push(vault_dir, env_file)
    result = preview_dotenv(vault_dir, PASSWORD, keys=["DB_HOST"])
    assert "DB_HOST=localhost" in result
    assert "DB_PORT" not in result


def test_preview_export_format(vault_dir, env_file):
    push(vault_dir, env_file)
    result = preview_export(vault_dir, PASSWORD)
    assert result.startswith("export ")
    assert "export DB_HOST=" in result


def test_preview_export_filtered(vault_dir, env_file):
    push(vault_dir, env_file)
    result = preview_export(vault_dir, PASSWORD, keys=["API_KEY"])
    assert "API_KEY" in result
    assert "DB_HOST" not in result


def test_preview_json_is_valid_json(vault_dir, env_file):
    push(vault_dir, env_file)
    result = preview_json(vault_dir, PASSWORD)
    data = json.loads(result)
    assert data["DB_HOST"] == "localhost"
    assert data["DB_PORT"] == "5432"


def test_preview_json_filtered(vault_dir, env_file):
    push(vault_dir, env_file)
    result = preview_json(vault_dir, PASSWORD, keys=["DB_PORT"])
    data = json.loads(result)
    assert list(data.keys()) == ["DB_PORT"]


def test_preview_dispatch_dotenv(vault_dir, env_file):
    push(vault_dir, env_file)
    result = preview(vault_dir, PASSWORD, fmt="dotenv")
    assert "DB_HOST" in result


def test_preview_dispatch_export(vault_dir, env_file):
    push(vault_dir, env_file)
    result = preview(vault_dir, PASSWORD, fmt="export")
    assert "export DB_HOST" in result


def test_preview_dispatch_json(vault_dir, env_file):
    push(vault_dir, env_file)
    result = preview(vault_dir, PASSWORD, fmt="json")
    assert json.loads(result)["API_KEY"] == "abc123"


def test_preview_unknown_format_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(PreviewError, match="Unknown format"):
        preview(vault_dir, PASSWORD, fmt="yaml")


def test_preview_specific_version(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    env2 = tmp_path / ".env2"
    env2.write_text("NEW_KEY=hello\n")
    push(vault_dir, str(env2))
    result = preview_dotenv(vault_dir, PASSWORD, version=1)
    assert "DB_HOST" in result
    assert "NEW_KEY" not in result
