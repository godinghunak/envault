"""Tests for envault.env_inheritance."""
from __future__ import annotations

import pytest

from envault.env_inheritance import inherit_dicts, InheritanceResult


PARENT = {"HOST": "localhost", "PORT": "5432", "DB": "prod"}
CHILD = {"HOST": "staging.example.com", "DEBUG": "true"}


def test_inherit_dicts_child_overrides_parent_key():
    result = inherit_dicts(PARENT, CHILD)
    assert result.merged["HOST"] == "staging.example.com"


def test_inherit_dicts_parent_key_inherited_when_absent_in_child():
    result = inherit_dicts(PARENT, CHILD)
    assert result.merged["PORT"] == "5432"
    assert result.merged["DB"] == "prod"


def test_inherit_dicts_child_only_key_present():
    result = inherit_dicts(PARENT, CHILD)
    assert result.merged["DEBUG"] == "true"
    assert "DEBUG" in result.child_only


def test_inherit_dicts_overridden_list_correct():
    result = inherit_dicts(PARENT, CHILD)
    assert "HOST" in result.overridden
    assert "PORT" not in result.overridden


def test_inherit_dicts_inherited_list_correct():
    result = inherit_dicts(PARENT, CHILD)
    assert "PORT" in result.inherited
    assert "DB" in result.inherited
    assert "HOST" not in result.inherited


def test_inherit_dicts_empty_parent():
    result = inherit_dicts({}, CHILD)
    assert result.merged == CHILD
    assert result.inherited == []
    assert result.child_only == sorted(CHILD.keys())


def test_inherit_dicts_empty_child():
    result = inherit_dicts(PARENT, {})
    assert result.merged == PARENT
    assert result.overridden == []
    assert result.child_only == []


def test_inherit_dicts_both_empty():
    result = inherit_dicts({}, {})
    assert result.merged == {}


def test_inherit_dicts_exclude_key_not_in_merged():
    result = inherit_dicts(PARENT, CHILD, exclude=["PORT"])
    assert "PORT" not in result.merged


def test_inherit_dicts_exclude_does_not_affect_child_keys():
    result = inherit_dicts(PARENT, {"PORT": "9999"}, exclude=["PORT"])
    # child explicitly sets PORT; exclusion only prevents *inheriting* from parent
    assert result.merged["PORT"] == "9999"


def test_inherit_dicts_summary_contains_counts():
    result = inherit_dicts(PARENT, CHILD)
    summary = result.summary()
    assert "Merged keys" in summary
    assert "Inherited" in summary
    assert "Overridden" in summary
    assert "Child-only" in summary


def test_inherit_dicts_result_is_inheritance_result_instance():
    result = inherit_dicts(PARENT, CHILD)
    assert isinstance(result, InheritanceResult)
