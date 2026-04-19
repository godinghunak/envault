import pytest
from envault.env_format import format_env, parse_lines


SAMPLE = """# comment
DB_HOST=localhost
DB_PORT=5432
API_KEY='secret'

DEBUG=true
"""


def test_parse_lines_identifies_comment():
    parsed = parse_lines("# hello")
    assert parsed[0][0] == "comment"


def test_parse_lines_identifies_blank():
    parsed = parse_lines("")
    assert parsed[0][0] == "blank"


def test_parse_lines_identifies_pair():
    parsed = parse_lines("FOO=bar")
    assert parsed[0][0] == "pair"
    assert parsed[0][1] == "FOO"


def test_format_env_identity():
    text = "FOO=bar\nBAZ=qux"
    result = format_env(text)
    assert "FOO=bar" in result
    assert "BAZ=qux" in result


def test_format_env_sort_keys():
    text = "ZEBRA=1\nAPPLE=2\nMIDDLE=3"
    result = format_env(text, sort_keys=True)
    lines = [l for l in result.splitlines() if l.strip()]
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys, key=str.lower)


def test_format_env_uppercase_keys():
    text = "db_host=localhost\napi_key=secret"
    result = format_env(text, uppercase_keys=True)
    assert "DB_HOST=localhost" in result
    assert "API_KEY=secret" in result


def test_format_env_strip_double_quotes():
    text = 'API_KEY="my_secret"'
    result = format_env(text, strip_quotes=True)
    assert 'API_KEY=my_secret' in result


def test_format_env_strip_single_quotes():
    text = "API_KEY='my_secret'"
    result = format_env(text, strip_quotes=True)
    assert "API_KEY=my_secret" in result


def test_format_env_remove_blanks():
    text = "FOO=1\n\nBAR=2\n\n"
    result = format_env(text, remove_blanks=True)
    assert "\n\n" not in result
    assert "FOO=1" in result
    assert "BAR=2" in result


def test_format_env_preserves_comments():
    text = "# my comment\nFOO=1"
    result = format_env(text)
    assert "# my comment" in result


def test_format_env_combined_options():
    text = "zebra='z'\n# note\napple='a'"
    result = format_env(text, sort_keys=True, strip_quotes=True, uppercase_keys=True)
    assert "APPLE=a" in result
    assert "ZEBRA=z" in result
    lines = result.splitlines()
    pair_lines = [l for l in lines if "=" in l and not l.startswith("#")]
    assert pair_lines[0].startswith("APPLE")
    assert pair_lines[1].startswith("ZEBRA")
