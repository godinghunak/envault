"""Tests for envault.env_transform."""
import pytest

from envault.env_transform import (
    apply_transforms,
    list_transforms,
    TransformResult,
    BUILTIN_TRANSFORMS,
)


SAMPLE = {"db_host": "Localhost", "api_key": "  'secret'  ", "Port": "5432"}


def test_list_transforms_returns_all_builtins():
    rules = list_transforms()
    names = {r.name for r in rules}
    assert "uppercase_keys" in names
    assert "strip_quotes" in names
    assert "trim_whitespace" in names
    assert "lowercase_values" in names


def test_apply_uppercase_keys():
    result = apply_transforms({"db_host": "val", "Port": "5432"}, ["uppercase_keys"])
    assert "DB_HOST" in result.transformed
    assert "PORT" in result.transformed
    assert result.applied == ["uppercase_keys"]


def test_apply_strip_quotes_double():
    result = apply_transforms({"KEY": '"hello"'}, ["strip_quotes"])
    assert result.transformed["KEY"] == "hello"


def test_apply_strip_quotes_single():
    result = apply_transforms({"KEY": "'world'"}, ["strip_quotes"])
    assert result.transformed["KEY"] == "world"


def test_apply_strip_quotes_no_quotes_unchanged():
    result = apply_transforms({"KEY": "plain"}, ["strip_quotes"])
    assert result.transformed["KEY"] == "plain"


def test_apply_trim_whitespace():
    result = apply_transforms({"  KEY  ": "  value  "}, ["trim_whitespace"])
    assert "KEY" in result.transformed
    assert result.transformed["KEY"] == "value"


def test_apply_lowercase_values():
    result = apply_transforms({"HOST": "LOCALHOST"}, ["lowercase_values"])
    assert result.transformed["HOST"] == "localhost"


def test_apply_multiple_transforms_in_order():
    env = {"db_host": '"Localhost"'}
    result = apply_transforms(env, ["uppercase_keys", "strip_quotes", "lowercase_values"])
    assert "DB_HOST" in result.transformed
    assert result.transformed["DB_HOST"] == "localhost"
    assert len(result.applied) == 3


def test_apply_unknown_transform_raises():
    with pytest.raises(ValueError, match="Unknown transform"):
        apply_transforms({"K": "v"}, ["nonexistent_transform"])


def test_transform_result_changed_keys():
    env = {"key": "VALUE"}
    result = apply_transforms(env, ["lowercase_values"])
    assert "key" in result.changed_keys


def test_transform_result_unchanged_keys_not_in_changed():
    env = {"KEY": "value"}
    result = apply_transforms(env, ["uppercase_keys"])
    # KEY is already uppercase — no change
    assert "KEY" not in result.changed_keys


def test_apply_empty_env():
    result = apply_transforms({}, ["uppercase_keys", "trim_whitespace"])
    assert result.transformed == {}
    assert result.applied == ["uppercase_keys", "trim_whitespace"]


def test_apply_no_transforms():
    env = {"A": "1", "B": "2"}
    result = apply_transforms(env, [])
    assert result.transformed == env
    assert result.applied == []
