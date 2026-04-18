import pytest
import types
from envault.vault import init_vault
from envault.templates import add_template, render_template
from envault.commands import cmd_push


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(tmp_path)
    return tmp_path


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_URL=postgres://localhost/db\nSECRET=abc123\nPORT=5432\n")
    return f


def push(vault_dir, env_file, password="pass"):
    args = types.SimpleNamespace(
        vault_dir=vault_dir, env_file=env_file, password=password
    )
    cmd_push(args)


def test_render_template_returns_matching_keys(vault_dir, env_file):
    push(vault_dir, env_file)
    add_template(vault_dir, "db", ["DB_URL", "PORT"])
    result = render_template(vault_dir, "db", 1, "pass")
    assert "DB_URL" in result
    assert "PORT" in result
    assert "SECRET" not in result


def test_render_template_correct_values(vault_dir, env_file):
    push(vault_dir, env_file)
    add_template(vault_dir, "db", ["DB_URL"])
    result = render_template(vault_dir, "db", 1, "pass")
    assert result["DB_URL"] == "postgres://localhost/db"


def test_render_template_missing_key_skipped(vault_dir, env_file):
    push(vault_dir, env_file)
    add_template(vault_dir, "partial", ["DB_URL", "NONEXISTENT"])
    result = render_template(vault_dir, "partial", 1, "pass")
    assert "DB_URL" in result
    assert "NONEXISTENT" not in result


def test_render_template_unknown_template_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(KeyError):
        render_template(vault_dir, "ghost", 1, "pass")
