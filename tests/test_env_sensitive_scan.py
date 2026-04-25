"""Tests for envault.env_sensitive_scan."""

import pytest
from envault.env_sensitive_scan import (
    _is_sensitive_key,
    _looks_like_real_secret,
    scan_dict,
    scan_versions,
    format_findings,
    SensitiveFinding,
)


# --- _is_sensitive_key ---

def test_is_sensitive_key_password():
    assert _is_sensitive_key("DB_PASSWORD") is True

def test_is_sensitive_key_api_key():
    assert _is_sensitive_key("STRIPE_API_KEY") is True

def test_is_sensitive_key_token():
    assert _is_sensitive_key("AUTH_TOKEN") is True

def test_is_sensitive_key_normal():
    assert _is_sensitive_key("APP_PORT") is False

def test_is_sensitive_key_secret_substring():
    assert _is_sensitive_key("CLIENT_SECRET") is True


# --- _looks_like_real_secret ---

def test_looks_like_real_secret_hex():
    assert _looks_like_real_secret("a3f1c9d2e8b047a1c3e5d7f9a2b4c6d8") is True

def test_looks_like_real_secret_base64():
    assert _looks_like_real_secret("dGhpcyBpcyBhIHRlc3Qgc2VjcmV0IGtleQ==") is True

def test_looks_like_real_secret_jwt():
    token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyIn0.abc"
    assert _looks_like_real_secret(token) is True

def test_looks_like_real_secret_placeholder():
    assert _looks_like_real_secret("<YOUR_SECRET_HERE>") is False

def test_looks_like_real_secret_short():
    assert _looks_like_real_secret("abc") is False

def test_looks_like_real_secret_empty():
    assert _looks_like_real_secret("") is False

def test_looks_like_real_secret_plain_word():
    assert _looks_like_real_secret("mysimplepassword") is False


# --- scan_dict ---

def test_scan_dict_finds_sensitive():
    env = {"DB_PASSWORD": "a3f1c9d2e8b047a1c3e5d7f9a2b4c6d8"}
    findings = scan_dict(env, version=1)
    assert len(findings) == 1
    assert findings[0].key == "DB_PASSWORD"
    assert findings[0].version == 1

def test_scan_dict_ignores_non_sensitive_key():
    env = {"APP_PORT": "a3f1c9d2e8b047a1c3e5d7f9a2b4c6d8"}
    findings = scan_dict(env, version=1)
    assert findings == []

def test_scan_dict_ignores_placeholder_value():
    env = {"DB_PASSWORD": "<change_me>"}
    findings = scan_dict(env, version=1)
    assert findings == []

def test_scan_dict_multiple_findings():
    env = {
        "API_KEY": "a3f1c9d2e8b047a1c3e5d7f9a2b4c6d8",
        "AUTH_TOKEN": "dGhpcyBpcyBhIHRlc3Qgc2VjcmV0IGtleQ==",
        "APP_NAME": "myapp",
    }
    findings = scan_dict(env, version=2)
    assert len(findings) == 2


# --- scan_versions ---

def test_scan_versions_aggregates_across_versions():
    versions = {
        1: {"DB_PASSWORD": "a3f1c9d2e8b047a1c3e5d7f9a2b4c6d8"},
        2: {"API_KEY": "dGhpcyBpcyBhIHRlc3Qgc2VjcmV0IGtleQ=="},
    }
    findings = scan_versions(versions)
    assert len(findings) == 2
    assert {f.version for f in findings} == {1, 2}

def test_scan_versions_empty_vault():
    assert scan_versions({}) == []


# --- format_findings ---

def test_format_findings_no_findings():
    assert format_findings([]) == "No sensitive values detected."

def test_format_findings_with_findings():
    f = SensitiveFinding(key="DB_PASSWORD", version=1, reason="test")
    output = format_findings([f])
    assert "1 sensitive finding" in output
    assert "DB_PASSWORD" in output
