import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.env_pin import set_pin, get_pin, remove_pin, list_pins
from envault.crypto import encrypt

PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\nFOO=bar\n")
    return str(f)


def push(vault_dir, env_file):
    from envault.vault import add_version
    content = Path(env_file).read_bytes()
    ciphertext = encrypt(content, PASSWORD)
    add_version(vault_dir, ciphertext)


def test_list_pins_empty(vault_dir):
    assert list_pins(vault_dir) == {}


def test_set_pin_stores_version(vault_dir, env_file):
    push(vault_dir, env_file)
    set_pin(vault_dir, 1)
    assert get_pin(vault_dir) == 1


def test_set_pin_custom_label(vault_dir, env_file):
    push(vault_dir, env_file)
    set_pin(vault_dir, 1, label="production")
    assert get_pin(vault_dir, label="production") == 1


def test_get_pin_missing_label_returns_none(vault_dir):
    assert get_pin(vault_dir, label="nonexistent") is None


def test_set_pin_invalid_version_raises(vault_dir):
    with pytest.raises(ValueError, match="does not exist"):
        set_pin(vault_dir, 99)


def test_remove_pin_returns_true(vault_dir, env_file):
    push(vault_dir, env_file)
    set_pin(vault_dir, 1)
    assert remove_pin(vault_dir) is True
    assert get_pin(vault_dir) is None


def test_remove_pin_missing_label_returns_false(vault_dir):
    assert remove_pin(vault_dir, label="ghost") is False


def test_list_pins_shows_all(vault_dir, env_file):
    push(vault_dir, env_file)
    set_pin(vault_dir, 1, label="stable")
    set_pin(vault_dir, 1, label="prod")
    pins = list_pins(vault_dir)
    assert pins["stable"] == 1
    assert pins["prod"] == 1
