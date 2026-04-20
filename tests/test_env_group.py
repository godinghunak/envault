"""Tests for envault.env_group."""

from __future__ import annotations

import pytest

from envault.env_group import (
    format_groups,
    get_group,
    group_by_custom,
    group_by_prefix,
    list_groups,
)

SAMPLE_ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "AWS_KEY": "abc",
    "AWS_SECRET": "xyz",
    "DEBUG": "true",
    "PORT": "8080",
}


def test_group_by_prefix_separates_correctly():
    grouped = group_by_prefix(SAMPLE_ENV)
    assert "DB" in grouped
    assert "AWS" in grouped
    assert grouped["DB"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert grouped["AWS"] == {"AWS_KEY": "abc", "AWS_SECRET": "xyz"}


def test_group_by_prefix_no_separator_goes_to_other():
    grouped = group_by_prefix(SAMPLE_ENV)
    assert "_OTHER" in grouped
    assert "DEBUG" in grouped["_OTHER"]
    assert "PORT" in grouped["_OTHER"]


def test_group_by_prefix_empty_env():
    grouped = group_by_prefix({})
    assert grouped == {}


def test_group_by_prefix_custom_separator():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432", "PLAIN": "value"}
    grouped = group_by_prefix(env, separator=".")
    assert "DB" in grouped
    assert "_OTHER" in grouped
    assert "PLAIN" in grouped["_OTHER"]


def test_group_by_custom_rules():
    rules = [("database", ["DB_"]), ("cloud", ["AWS_"])]
    grouped = group_by_custom(SAMPLE_ENV, rules)
    assert "database" in grouped
    assert "cloud" in grouped
    assert grouped["database"]["DB_HOST"] == "localhost"
    assert grouped["cloud"]["AWS_KEY"] == "abc"


def test_group_by_custom_unmatched_goes_to_other():
    rules = [("database", ["DB_"])]
    grouped = group_by_custom(SAMPLE_ENV, rules)
    assert "_OTHER" in grouped
    assert "AWS_KEY" in grouped["_OTHER"]
    assert "DEBUG" in grouped["_OTHER"]


def test_group_by_custom_empty_rules():
    grouped = group_by_custom(SAMPLE_ENV, [])
    assert list(grouped.keys()) == ["_OTHER"]
    assert len(grouped["_OTHER"]) == len(SAMPLE_ENV)


def test_list_groups_sorted():
    grouped = group_by_prefix(SAMPLE_ENV)
    names = list_groups(grouped)
    assert names == sorted(names)


def test_get_group_existing():
    grouped = group_by_prefix(SAMPLE_ENV)
    db = get_group(grouped, "DB")
    assert db is not None
    assert "DB_HOST" in db


def test_get_group_missing_returns_none():
    grouped = group_by_prefix(SAMPLE_ENV)
    assert get_group(grouped, "NONEXISTENT") is None


def test_format_groups_contains_group_headers():
    grouped = group_by_prefix(SAMPLE_ENV)
    output = format_groups(grouped)
    assert "[DB]" in output
    assert "[AWS]" in output
    assert "DB_HOST=localhost" in output
