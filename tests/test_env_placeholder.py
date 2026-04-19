import pytest
from envault.env_placeholder import (
    is_placeholder,
    find_placeholders,
    find_placeholders_in_text,
    PlaceholderIssue,
)


def test_is_placeholder_angle_brackets():
    assert is_placeholder('<YOUR_SECRET>') is not None


def test_is_placeholder_double_curly():
    assert is_placeholder('{{MY_TOKEN}}') is not None


def test_is_placeholder_change_me():
    assert is_placeholder('CHANGE_ME') is not None


def test_is_placeholder_todo():
    assert is_placeholder('TODO') is not None


def test_is_placeholder_your_prefix():
    assert is_placeholder('YOUR_API_KEY') is not None


def test_is_placeholder_dollar_brace():
    assert is_placeholder('${SECRET}') is not None


def test_is_placeholder_normal_value():
    assert is_placeholder('supersecret123') is None


def test_is_placeholder_empty_string():
    assert is_placeholder('') is None


def test_find_placeholders_returns_issues():
    env = {'API_KEY': '<YOUR_API_KEY>', 'DB_PASS': 'realpass'}
    issues = find_placeholders(env)
    assert len(issues) == 1
    assert issues[0].key == 'API_KEY'


def test_find_placeholders_no_issues():
    env = {'API_KEY': 'abc123', 'DB_PASS': 'hunter2'}
    assert find_placeholders(env) == []


def test_find_placeholders_multiple():
    env = {'A': 'CHANGE_ME', 'B': '{{TOKEN}}', 'C': 'real'}
    issues = find_placeholders(env)
    assert len(issues) == 2


def test_find_placeholders_in_text_basic():
    text = 'API_KEY=<YOUR_KEY>\nDB_HOST=localhost\n'
    issues = find_placeholders_in_text(text)
    assert len(issues) == 1
    assert issues[0].key == 'API_KEY'


def test_find_placeholders_in_text_ignores_comments():
    text = '# API_KEY=<YOUR_KEY>\nDB_HOST=localhost\n'
    issues = find_placeholders_in_text(text)
    assert issues == []


def test_placeholder_issue_str():
    issue = PlaceholderIssue(key='FOO', value='<BAR>', pattern=r'^<.+>$')
    s = str(issue)
    assert 'FOO' in s
    assert '<BAR>' in s
