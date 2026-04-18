import pytest
from envault.templates import (
    add_template, remove_template, get_template, list_templates,
    load_templates, template_from_env_content, render_template
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_load_templates_empty(vault_dir):
    assert load_templates(vault_dir) == {}


def test_add_template(vault_dir):
    add_template(vault_dir, "base", ["DB_HOST", "DB_PORT"])
    assert "base" in load_templates(vault_dir)


def test_list_templates(vault_dir):
    add_template(vault_dir, "base", ["A"])
    add_template(vault_dir, "prod", ["B"])
    names = list_templates(vault_dir)
    assert "base" in names
    assert "prod" in names


def test_get_template(vault_dir):
    add_template(vault_dir, "base", ["DB_HOST", "DB_PORT"])
    keys = get_template(vault_dir, "base")
    assert keys == ["DB_HOST", "DB_PORT"]


def test_get_template_missing_raises(vault_dir):
    with pytest.raises(KeyError):
        get_template(vault_dir, "nonexistent")


def test_remove_template(vault_dir):
    add_template(vault_dir, "base", ["A"])
    remove_template(vault_dir, "base")
    assert "base" not in list_templates(vault_dir)


def test_remove_template_missing_raises(vault_dir):
    with pytest.raises(KeyError):
        remove_template(vault_dir, "ghost")


def test_template_from_env_content():
    content = "# comment\nDB_HOST=localhost\nDB_PORT=5432\n\nSECRET=abc\n"
    keys = template_from_env_content(content)
    assert keys == ["DB_HOST", "DB_PORT", "SECRET"]


def test_template_from_env_content_ignores_blanks_and_comments():
    content = "\n# ignore\nKEY=val\n"
    assert template_from_env_content(content) == ["KEY"]


def test_render_template():
    keys = ["HOST", "PORT", "SECRET"]
    rendered = render_template(keys)
    assert "HOST=" in rendered
    assert "PORT=" in rendered
    assert "SECRET=" in rendered
    for line in rendered.strip().splitlines():
        assert line.endswith("=")
