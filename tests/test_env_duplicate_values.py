"""Tests for envault.env_duplicate_values."""

import pytest

from envault.env_duplicate_values import (
    DuplicateValueGroup,
    find_duplicate_values,
    format_duplicate_values,
)


ENV_NO_DUPES = """DB_HOST=localhost
DB_PORT=5432
APP_NAME=myapp
"""

ENV_WITH_DUPES = """SECRET_A=abc123
SECRET_B=abc123
DB_HOST=localhost
DB_BACKUP_HOST=localhost
APP_NAME=myapp
"""

ENV_EMPTY_VALUES = """KEY_A=
KEY_B=
KEY_C=hello
"""

ENV_TRIPLE_DUPE = """X=same
Y=same
Z=same
"""


def test_find_duplicate_values_no_dupes():
    groups = find_duplicate_values(ENV_NO_DUPES)
    assert groups == []


def test_find_duplicate_values_finds_two_groups():
    groups = find_duplicate_values(ENV_WITH_DUPES)
    assert len(groups) == 2


def test_find_duplicate_values_correct_keys():
    groups = find_duplicate_values(ENV_WITH_DUPES)
    all_key_sets = [frozenset(g.keys) for g in groups]
    assert frozenset({"SECRET_A", "SECRET_B"}) in all_key_sets
    assert frozenset({"DB_HOST", "DB_BACKUP_HOST"}) in all_key_sets


def test_find_duplicate_values_ignores_empty_values():
    groups = find_duplicate_values(ENV_EMPTY_VALUES)
    assert groups == []


def test_find_duplicate_values_triple_dupe():
    groups = find_duplicate_values(ENV_TRIPLE_DUPE)
    assert len(groups) == 1
    assert set(groups[0].keys) == {"X", "Y", "Z"}


def test_find_duplicate_values_empty_text():
    groups = find_duplicate_values("")
    assert groups == []


def test_find_duplicate_values_ignores_comments():
    text = "# DB_HOST=localhost\nDB_HOST=localhost\nOTHER=localhost\n"
    groups = find_duplicate_values(text)
    assert len(groups) == 1
    assert set(groups[0].keys) == {"DB_HOST", "OTHER"}


def test_format_duplicate_values_no_dupes():
    result = format_duplicate_values([])
    assert result == "No duplicate values found."


def test_format_duplicate_values_contains_keys():
    groups = find_duplicate_values(ENV_WITH_DUPES)
    output = format_duplicate_values(groups)
    assert "SECRET_A" in output
    assert "SECRET_B" in output
    assert "DB_HOST" in output
    assert "DB_BACKUP_HOST" in output


def test_format_duplicate_values_header():
    groups = find_duplicate_values(ENV_WITH_DUPES)
    output = format_duplicate_values(groups)
    assert output.startswith("Duplicate values detected:")


def test_duplicate_value_group_str_truncates_long_value():
    long_val = "x" * 60
    g = DuplicateValueGroup(value=long_val, keys=["A", "B"])
    s = str(g)
    assert "..." in s
    assert "A" in s
    assert "B" in s
