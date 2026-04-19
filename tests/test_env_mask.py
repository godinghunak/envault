import pytest
from envault.env_mask import is_sensitive, mask_value, mask_dict, mask_env_text


def test_is_sensitive_password():
    assert is_sensitive("PASSWORD") is True


def test_is_sensitive_api_key():
    assert is_sensitive("API_KEY") is True


def test_is_sensitive_token():
    assert is_sensitive("AUTH_TOKEN") is True


def test_is_sensitive_normal_key():
    assert is_sensitive("APP_NAME") is False


def test_is_sensitive_db_host():
    assert is_sensitive("DB_HOST") is False


def test_mask_value_full():
    assert mask_value("supersecret") == "****"


def test_mask_value_show_chars():
    result = mask_value("supersecret", show_chars=3)
    assert result == "****ret"


def test_mask_value_empty():
    assert mask_value("") == "****"


def test_mask_value_custom_mask():
    assert mask_value("abc", mask="[HIDDEN]") == "[HIDDEN]"


def test_mask_dict_masks_sensitive():
    env = {"APP_NAME": "myapp", "DB_PASSWORD": "secret123"}
    result = mask_dict(env)
    assert result["APP_NAME"] == "myapp"
    assert result["DB_PASSWORD"] == "****"


def test_mask_dict_explicit_keys():
    env = {"APP_NAME": "myapp", "DB_HOST": "localhost"}
    result = mask_dict(env, keys=["DB_HOST"])
    assert result["APP_NAME"] == "myapp"
    assert result["DB_HOST"] == "****"


def test_mask_dict_show_chars():
    env = {"API_KEY": "abcdef1234"}
    result = mask_dict(env, show_chars=4)
    assert result["API_KEY"] == "****1234"


def test_mask_env_text_masks_sensitive_lines():
    text = "APP_NAME=myapp\nDB_PASSWORD=secret\n"
    result = mask_env_text(text)
    assert "APP_NAME=myapp" in result
    assert "DB_PASSWORD=****" in result


def test_mask_env_text_preserves_comments():
    text = "# comment\nAPP=val\n"
    result = mask_env_text(text)
    assert "# comment" in result


def test_mask_env_text_preserves_blanks():
    text = "A=1\n\nB=2\n"
    result = mask_env_text(text)
    assert "A=1" in result
    assert "B=2" in result


def test_mask_env_text_show_chars():
    text = "SECRET_KEY=abcdefgh\n"
    result = mask_env_text(text, show_chars=3)
    assert "****fgh" in result
