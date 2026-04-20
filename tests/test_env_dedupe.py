"""Tests for envault.env_dedupe."""
import pytest
from envault.env_dedupe import find_duplicates, dedupe_env, DuplicateKey


ENV_NO_DUPES = """HOST=localhost
PORT=5432
DB=mydb
"""

ENV_WITH_DUPES = """HOST=localhost
PORT=5432
HOST=remotehost
DB=mydb
PORT=9999
"""

ENV_WITH_COMMENT = """# HOST is set below
HOST=localhost
PORT=5432
HOST=remotehost
"""


def test_find_duplicates_no_dupes():
    result = find_duplicates(ENV_NO_DUPES)
    assert result == []


def test_find_duplicates_finds_two_keys():
    result = find_duplicates(ENV_WITH_DUPES)
    keys = {d.key for d in result}
    assert "HOST" in keys
    assert "PORT" in keys


def test_find_duplicates_correct_line_numbers():
    result = find_duplicates(ENV_WITH_DUPES)
    host = next(d for d in result if d.key == "HOST")
    assert host.line_numbers == [1, 3]


def test_find_duplicates_correct_values():
    result = find_duplicates(ENV_WITH_DUPES)
    host = next(d for d in result if d.key == "HOST")
    assert host.values == ["localhost", "remotehost"]


def test_find_duplicates_ignores_comments():
    result = find_duplicates(ENV_WITH_COMMENT)
    assert len(result) == 1
    assert result[0].key == "HOST"


def test_duplicate_key_str():
    d = DuplicateKey("FOO", [1, 4], ["a", "b"])
    s = str(d)
    assert "FOO" in s
    assert "1" in s
    assert "4" in s


def test_dedupe_keep_last():
    cleaned = dedupe_env(ENV_WITH_DUPES, keep="last")
    lines = [l for l in cleaned.splitlines() if l.startswith("HOST")]
    assert len(lines) == 1
    assert lines[0] == "HOST=remotehost"


def test_dedupe_keep_first():
    cleaned = dedupe_env(ENV_WITH_DUPES, keep="first")
    lines = [l for l in cleaned.splitlines() if l.startswith("HOST")]
    assert len(lines) == 1
    assert lines[0] == "HOST=localhost"


def test_dedupe_preserves_non_duplicate_keys():
    cleaned = dedupe_env(ENV_WITH_DUPES, keep="last")
    assert "DB=mydb" in cleaned


def test_dedupe_no_dupes_unchanged():
    cleaned = dedupe_env(ENV_NO_DUPES)
    assert cleaned == ENV_NO_DUPES


def test_dedupe_invalid_keep_raises():
    with pytest.raises(ValueError):
        dedupe_env(ENV_WITH_DUPES, keep="middle")


def test_dedupe_preserves_comments():
    cleaned = dedupe_env(ENV_WITH_COMMENT, keep="last")
    assert "# HOST is set below" in cleaned
