"""Tests for envault.env_resolve."""
import pytest
from envault.env_resolve import (
    resolve_references,
    format_resolve_result,
    ResolutionError,
    ResolveResult,
    _expand,
)


def test_resolve_no_references():
    base = {"HOST": "localhost", "PORT": "5432"}
    result = resolve_references(base)
    assert result.ok
    assert result.resolved["HOST"] == "localhost"
    assert result.resolved["PORT"] == "5432"


def test_resolve_simple_reference():
    base = {"HOST": "localhost", "URL": "http://${HOST}:8080"}
    result = resolve_references(base)
    assert result.ok
    assert result.resolved["URL"] == "http://localhost:8080"


def test_resolve_chained_references():
    base = {"A": "hello", "B": "${A}_world", "C": "${B}!"}
    result = resolve_references(base)
    assert result.ok
    assert result.resolved["C"] == "hello_world!"


def test_resolve_missing_reference_non_strict():
    base = {"URL": "http://${MISSING}:8080"}
    result = resolve_references(base, strict=False)
    assert not result.ok
    assert len(result.errors) == 1
    assert result.errors[0].key == "URL"
    assert "MISSING" in result.errors[0].reason


def test_resolve_missing_reference_strict_raises():
    base = {"URL": "http://${MISSING}:8080"}
    with pytest.raises(ValueError, match="MISSING"):
        resolve_references(base, strict=True)


def test_resolve_override_wins():
    base = {"HOST": "localhost", "URL": "http://${HOST}"}
    overrides = {"HOST": "example.com"}
    result = resolve_references(base, overrides)
    assert result.ok
    assert result.resolved["URL"] == "http://example.com"


def test_resolve_override_adds_key():
    base = {"A": "1"}
    overrides = {"B": "2"}
    result = resolve_references(base, overrides)
    assert result.ok
    assert result.resolved["B"] == "2"


def test_expand_no_refs():
    assert _expand("hello", {}) == "hello"


def test_expand_single_ref():
    assert _expand("${X}", {"X": "42"}) == "42"


def test_expand_missing_raises():
    with pytest.raises(KeyError):
        _expand("${NOPE}", {})


def test_format_resolve_result_no_errors():
    result = ResolveResult(resolved={"A": "1", "B": "2"})
    output = format_resolve_result(result)
    assert "A=1" in output
    assert "B=2" in output
    assert "Errors" not in output


def test_format_resolve_result_with_errors():
    result = ResolveResult(
        resolved={"A": "1"},
        errors=[ResolutionError(key="B", reason="undefined reference ${X}")],
    )
    output = format_resolve_result(result)
    assert "Errors" in output
    assert "B" in output
