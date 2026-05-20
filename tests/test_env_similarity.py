"""Tests for envault.env_similarity."""
import pytest
from envault.env_similarity import compare_dicts, similarity_score, SimilarityResult


A = {"KEY_A": "1", "KEY_B": "2", "KEY_C": "3"}
B = {"KEY_A": "1", "KEY_B": "changed", "KEY_D": "4"}


def test_compare_dicts_common_keys():
    r = compare_dicts(A, B)
    assert set(r.common_keys) == {"KEY_A", "KEY_B"}


def test_compare_dicts_only_in_a():
    r = compare_dicts(A, B)
    assert r.only_in_a == ["KEY_C"]


def test_compare_dicts_only_in_b():
    r = compare_dicts(A, B)
    assert r.only_in_b == ["KEY_D"]


def test_compare_dicts_changed_keys():
    r = compare_dicts(A, B)
    assert r.changed_keys == ["KEY_B"]


def test_compare_dicts_unchanged_key_not_in_changed():
    r = compare_dicts(A, B)
    assert "KEY_A" not in r.changed_keys


def test_compare_dicts_key_similarity_range():
    r = compare_dicts(A, B)
    assert 0.0 <= r.key_similarity <= 1.0


def test_compare_dicts_value_similarity_range():
    r = compare_dicts(A, B)
    assert 0.0 <= r.value_similarity <= 1.0


def test_compare_identical_dicts_perfect_score():
    r = compare_dicts(A, A, version_a=1, version_b=2)
    assert r.key_similarity == 1.0
    assert r.value_similarity == 1.0
    assert r.changed_keys == []
    assert r.only_in_a == []
    assert r.only_in_b == []


def test_compare_empty_dicts():
    r = compare_dicts({}, {})
    assert r.key_similarity == 1.0
    assert r.value_similarity == 1.0


def test_compare_completely_different_dicts():
    r = compare_dicts({"X": "1"}, {"Y": "2"})
    assert r.key_similarity == 0.0
    assert r.value_similarity == 0.0


def test_similarity_score_is_average():
    r = compare_dicts(A, B)
    expected = (r.key_similarity + r.value_similarity) / 2.0
    assert similarity_score(r) == pytest.approx(expected)


def test_similarity_score_perfect():
    r = compare_dicts(A, A)
    assert similarity_score(r) == pytest.approx(1.0)


def test_str_contains_versions():
    r = compare_dicts(A, B, version_a=3, version_b=7)
    s = str(r)
    assert "3" in s
    assert "7" in s


def test_version_fields_stored():
    r = compare_dicts(A, B, version_a=5, version_b=9)
    assert r.version_a == 5
    assert r.version_b == 9
