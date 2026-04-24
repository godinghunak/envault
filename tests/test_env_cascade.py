"""Tests for envault.env_cascade."""
import pytest
from envault.env_cascade import cascade_dicts, format_cascade, CascadeResult


def test_cascade_dicts_single_layer():
    layers = [("base", {"A": "1", "B": "2"})]
    result = cascade_dicts(layers)
    assert result.merged == {"A": "1", "B": "2"}
    assert result.sources["A"] == "base"
    assert result.sources["B"] == "base"


def test_cascade_dicts_later_layer_wins():
    layers = [
        ("base", {"A": "1", "B": "2"}),
        ("override", {"B": "99", "C": "3"}),
    ]
    result = cascade_dicts(layers)
    assert result.merged["A"] == "1"
    assert result.merged["B"] == "99"
    assert result.merged["C"] == "3"
    assert result.sources["B"] == "override"
    assert result.sources["A"] == "base"


def test_cascade_dicts_three_layers():
    layers = [
        ("defaults", {"X": "a", "Y": "b", "Z": "c"}),
        ("staging", {"Y": "staging_b"}),
        ("prod", {"Z": "prod_c"}),
    ]
    result = cascade_dicts(layers)
    assert result.merged["X"] == "a"
    assert result.merged["Y"] == "staging_b"
    assert result.merged["Z"] == "prod_c"
    assert result.sources["Y"] == "staging"
    assert result.sources["Z"] == "prod"


def test_cascade_dicts_empty_layers():
    result = cascade_dicts([])
    assert result.merged == {}
    assert result.sources == {}


def test_cascade_dicts_empty_layer_in_middle():
    layers = [
        ("base", {"A": "1"}),
        ("empty", {}),
        ("top", {"B": "2"}),
    ]
    result = cascade_dicts(layers)
    assert result.merged == {"A": "1", "B": "2"}


def test_format_cascade_no_sources():
    result = CascadeResult(
        merged={"DB_HOST": "localhost", "APP_ENV": "prod"},
        sources={"DB_HOST": "base", "APP_ENV": "override"},
    )
    output = format_cascade(result, show_sources=False)
    assert "APP_ENV=prod" in output
    assert "DB_HOST=localhost" in output
    assert "# source:" not in output


def test_format_cascade_with_sources():
    result = CascadeResult(
        merged={"KEY": "val"},
        sources={"KEY": "prod"},
    )
    output = format_cascade(result, show_sources=True)
    assert "# source: prod" in output
    assert "KEY=val" in output


def test_format_cascade_sorted_keys():
    result = CascadeResult(
        merged={"Z": "last", "A": "first", "M": "mid"},
        sources={"Z": "x", "A": "x", "M": "x"},
    )
    output = format_cascade(result)
    lines = [l for l in output.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys)
