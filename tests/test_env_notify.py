import pytest
from unittest.mock import patch, MagicMock
from envault.vault import init_vault
from envault.env_notify import (
    load_notify_config,
    set_webhook,
    remove_webhook,
    get_webhook,
    send_notification,
)


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


def test_load_notify_config_empty(vault_dir):
    assert load_notify_config(vault_dir) == {}


def test_set_webhook_stores_url(vault_dir):
    set_webhook(vault_dir, "https://example.com/hook")
    assert get_webhook(vault_dir) == "https://example.com/hook"


def test_set_webhook_overwrites(vault_dir):
    set_webhook(vault_dir, "https://first.com")
    set_webhook(vault_dir, "https://second.com")
    assert get_webhook(vault_dir) == "https://second.com"


def test_remove_webhook(vault_dir):
    set_webhook(vault_dir, "https://example.com/hook")
    remove_webhook(vault_dir)
    assert get_webhook(vault_dir) is None


def test_remove_webhook_when_none_set(vault_dir):
    remove_webhook(vault_dir)  # should not raise
    assert get_webhook(vault_dir) is None


def test_send_notification_no_webhook_returns_false(vault_dir):
    result = send_notification(vault_dir, "push", {"version": 1})
    assert result is False


def test_send_notification_success(vault_dir):
    set_webhook(vault_dir, "https://example.com/hook")
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = send_notification(vault_dir, "push", {"version": 1})
    assert result is True


def test_send_notification_failure_returns_false(vault_dir):
    import urllib.error
    set_webhook(vault_dir, "https://example.com/hook")
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("err")):
        result = send_notification(vault_dir, "push", {"version": 1})
    assert result is False
