import pytest
from envault.env_flatten import (
    flatten_to_dict,
    expand_from_dict,
    list_prefixes,
    flatten_env_text,
    SEPARATOR,
)


def test_flatten_to_dict_single_level():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = flatten_to_dict(env)
    assert result == {"HOST": "localhost", "PORT": "5432"}


def test_flatten_to_dict_two_levels():
    env = {"DB__HOST": "localhost", "DB__PORT": "5432"}
    result = flatten_to_dict(env)
    assert result == {"DB": {"HOST": "localhost", "PORT": "5432"}}


def test_flatten_to_dict_three_levels():
    env = {"APP__DB__HOST": "localhost"}
    result = flatten_to_dict(env)
    assert result == {"APP": {"DB": {"HOST": "localhost"}}}


def test_flatten_to_dict_mixed_levels():
    env = {"DB__HOST": "localhost", "APP_NAME": "myapp"}
    result = flatten_to_dict(env)
    assert result["DB"] == {"HOST": "localhost"}
    assert result["APP_NAME"] == "myapp"


def test_flatten_to_dict_custom_separator():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432"}
    result = flatten_to_dict(env, sep=".")
    assert result == {"DB": {"HOST": "localhost", "PORT": "5432"}}


def test_expand_from_dict_simple():
    nested = {"HOST": "localhost", "PORT": "5432"}
    result = expand_from_dict(nested)
    assert result == {"HOST": "localhost", "PORT": "5432"}


def test_expand_from_dict_nested():
    nested = {"DB": {"HOST": "localhost", "PORT": "5432"}}
    result = expand_from_dict(nested)
    assert result == {"DB__HOST": "localhost", "DB__PORT": "5432"}


def test_expand_from_dict_three_levels():
    nested = {"APP": {"DB": {"HOST": "localhost"}}}
    result = expand_from_dict(nested)
    assert result == {"APP__DB__HOST": "localhost"}


def test_flatten_expand_roundtrip():
    env = {"DB__HOST": "localhost", "DB__PORT": "5432", "APP__NAME": "myapp"}
    nested = flatten_to_dict(env)
    recovered = expand_from_dict(nested)
    assert recovered == env


def test_list_prefixes_finds_groups():
    env = {"DB__HOST": "localhost", "DB__PORT": "5432", "APP__NAME": "myapp", "SIMPLE": "value"}
    prefixes = list_prefixes(env)
    assert "DB" in prefixes
    assert "APP" in prefixes
    assert "SIMPLE" not in prefixes


def test_list_prefixes_empty():
    assert list_prefixes({}) == []


def test_list_prefixes_no_separator():
    env = {"HOST": "localhost", "PORT": "5432"}
    assert list_prefixes(env) == []


def test_flatten_env_text_basic():
    text = "DB__HOST=localhost\nDB__PORT=5432\n"
    result = flatten_env_text(text)
    assert result == {"DB": {"HOST": "localhost", "PORT": "5432"}}


def test_flatten_env_text_ignores_comments():
    text = "# comment\nDB__HOST=localhost\n"
    result = flatten_env_text(text)
    assert "DB" in result
    assert "# comment" not in str(result)


def test_flatten_env_text_ignores_blank_lines():
    text = "\nDB__HOST=localhost\n\n"
    result = flatten_env_text(text)
    assert result == {"DB": {"HOST": "localhost"}}
