"""Tests for envault.env_crossref."""
import pytest

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_crossref import crossref_versions, format_crossref, CrossRefResult


@pytest.fixture
def vault_dir(tmp_path):
    vd = str(tmp_path / ".envault")
    init_vault(vd)
    return vd


@pytest.fixture
def env_file(tmp_path):
    return tmp_path / ".env"


def push(vault_dir, env_file, password, content):
    env_file.write_text(content)

    class Args:
        pass

    a = Args()
    a.vault_dir = vault_dir
    a.env_file = str(env_file)
    a.password = password
    cmd_push(a)


def test_crossref_identical_versions(vault_dir, env_file):
    content = "KEY_A=1\nKEY_B=2\n"
    push(vault_dir, env_file, "pw", content)
    push(vault_dir, env_file, "pw", content)
    result = crossref_versions(vault_dir, "pw", 1, 2)
    assert result.ok
    assert result.issues == []


def test_crossref_detects_key_added_in_b(vault_dir, env_file):
    push(vault_dir, env_file, "pw", "KEY_A=1\n")
    push(vault_dir, env_file, "pw", "KEY_A=1\nKEY_B=2\n")
    result = crossref_versions(vault_dir, "pw", 1, 2)
    assert not result.ok
    assert len(result.only_in_b()) == 1
    assert result.only_in_b()[0].key == "KEY_B"


def test_crossref_detects_key_removed_in_b(vault_dir, env_file):
    push(vault_dir, env_file, "pw", "KEY_A=1\nKEY_B=2\n")
    push(vault_dir, env_file, "pw", "KEY_A=1\n")
    result = crossref_versions(vault_dir, "pw", 1, 2)
    assert not result.ok
    assert len(result.only_in_a()) == 1
    assert result.only_in_a()[0].key == "KEY_B"


def test_crossref_symmetric_issues(vault_dir, env_file):
    push(vault_dir, env_file, "pw", "KEY_A=1\nKEY_B=2\n")
    push(vault_dir, env_file, "pw", "KEY_B=2\nKEY_C=3\n")
    result = crossref_versions(vault_dir, "pw", 1, 2)
    assert not result.ok
    only_a_keys = {i.key for i in result.only_in_a()}
    only_b_keys = {i.key for i in result.only_in_b()}
    assert "KEY_A" in only_a_keys
    assert "KEY_C" in only_b_keys


def test_format_crossref_ok():
    result = CrossRefResult(version_a=1, version_b=2)
    output = format_crossref(result)
    assert "No cross-reference issues" in output
    assert "v1" in output
    assert "v2" in output


def test_format_crossref_with_issues(vault_dir, env_file):
    push(vault_dir, env_file, "pw", "KEY_A=1\n")
    push(vault_dir, env_file, "pw", "KEY_A=1\nKEY_B=2\n")
    result = crossref_versions(vault_dir, "pw", 1, 2)
    output = format_crossref(result)
    assert "KEY_B" in output
    assert "v1" in output
    assert "v2" in output
