"""Tests for envault.env_variables."""

import pytest
from envault.env_variables import (
    find_references,
    substitute,
    resolve_env,
    find_unresolved,
    SubstitutionError,
)


def test_find_references_none():
    assert find_references("hello world") == []


def test_find_references_single():
    assert find_references("http://${HOST}:8080") == ["HOST"]


def test_find_references_multiple():
    refs = find_references("${SCHEME}://${HOST}:${PORT}")
    assert refs == ["SCHEME", "HOST", "PORT"]


def test_find_references_no_bare_dollar():
    assert find_references("$HOME") == []


def test_substitute_simple():
    result = substitute("${GREETING} world", {"GREETING": "hello"})
    assert result == "hello world"


def test_substitute_multiple():
    result = substitute("${A}-${B}", {"A": "foo", "B": "bar"})
    assert result == "foo-bar"


def test_substitute_missing_raises():
    with pytest.raises(SubstitutionError) as exc_info:
        substitute("${MISSING}", {}, key="MY_KEY")
    assert "MY_KEY" in str(exc_info.value)
    assert "MISSING" in str(exc_info.value)


def test_resolve_env_no_refs():
    env = {"A": "1", "B": "2"}
    assert resolve_env(env) == env


def test_resolve_env_simple_ref():
    env = {"HOST": "localhost", "URL": "http://${HOST}/api"}
    result = resolve_env(env)
    assert result["URL"] == "http://localhost/api"


def test_resolve_env_chain():
    env = {"BASE": "example.com", "HOST": "db.${BASE}", "DSN": "postgres://${HOST}"}
    result = resolve_env(env)
    assert result["HOST"] == "db.example.com"
    assert result["DSN"] == "postgres://db.example.com"


def test_resolve_env_strict_raises_on_missing():
    env = {"URL": "http://${UNDEFINED}"}
    with pytest.raises(SubstitutionError):
        resolve_env(env, strict=True)


def test_resolve_env_lenient_leaves_unresolved():
    env = {"URL": "http://${UNDEFINED}"}
    result = resolve_env(env, strict=False)
    assert result["URL"] == "http://${UNDEFINED}"


def test_find_unresolved_empty():
    env = {"A": "1", "B": "${A}"}
    assert find_unresolved(env) == []


def test_find_unresolved_detects_missing():
    env = {"A": "${GHOST}"}
    assert find_unresolved(env) == ["A"]


def test_find_unresolved_multiple_keys():
    env = {"A": "${X}", "B": "${Y}", "C": "clean"}
    bad = find_unresolved(env)
    assert set(bad) == {"A", "B"}
