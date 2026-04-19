import pytest
from envault.env_tokenize import detect_type, tokenize_env, tokenize_dict, group_by_type, Token


def test_detect_type_integer():
    assert detect_type("42") == "integer"


def test_detect_type_float():
    assert detect_type("3.14") == "float"


def test_detect_type_boolean_true():
    assert detect_type("true") == "boolean"


def test_detect_type_boolean_false():
    assert detect_type("false") == "boolean"


def test_detect_type_url():
    assert detect_type("https://example.com/path") == "url"


def test_detect_type_email():
    assert detect_type("user@example.com") == "email"


def test_detect_type_hex():
    assert detect_type("deadbeefcafe1234") == "hex"


def test_detect_type_path():
    assert detect_type("/var/log/app") == "path"


def test_detect_type_string_fallback():
    assert detect_type("hello world") == "string"


def test_tokenize_env_basic():
    text = "PORT=8080\nDEBUG=true\nNAME=myapp"
    tokens = tokenize_env(text)
    assert len(tokens) == 3
    assert tokens[0].key == "PORT"
    assert tokens[0].token_type == "integer"
    assert tokens[1].token_type == "boolean"
    assert tokens[2].token_type == "string"


def test_tokenize_env_ignores_comments():
    text = "# comment\nKEY=value"
    tokens = tokenize_env(text)
    assert len(tokens) == 1


def test_tokenize_env_ignores_blank_lines():
    text = "\n\nKEY=value\n\n"
    tokens = tokenize_env(text)
    assert len(tokens) == 1


def test_tokenize_env_strips_quotes():
    text = 'DB_URL="https://db.example.com"'
    tokens = tokenize_env(text)
    assert tokens[0].token_type == "url"


def test_tokenize_env_skips_missing_equals():
    text = "NOEQUALS\nKEY=val"
    tokens = tokenize_env(text)
    assert len(tokens) == 1


def test_tokenize_dict():
    d = {"PORT": "3000", "HOST": "localhost"}
    tokens = tokenize_dict(d)
    assert len(tokens) == 2
    types = {t.key: t.token_type for t in tokens}
    assert types["PORT"] == "integer"
    assert types["HOST"] == "string"


def test_group_by_type():
    tokens = [
        Token("A", "1", "integer"),
        Token("B", "2", "integer"),
        Token("C", "hello", "string"),
    ]
    groups = group_by_type(tokens)
    assert len(groups["integer"]) == 2
    assert len(groups["string"]) == 1


def test_token_str():
    t = Token("KEY", "val", "string")
    assert "KEY" in str(t)
    assert "string" in str(t)
