"""Tests for envault.commands_similarity.cmd_similarity."""
import argparse
import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_similarity import cmd_similarity


@pytest.fixture()
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    init_vault(str(d))
    return str(d)


@pytest.fixture()
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY_A=hello\nKEY_B=world\n")
    return str(f)


def push(vault_dir, env_file, password="secret"):
    ns = argparse.Namespace(
        vault_dir=vault_dir, env_file=env_file, password=password
    )
    cmd_push(ns)


def make_args(vault_dir, password="secret", v_a=None, v_b=None, show_keys=False):
    return argparse.Namespace(
        vault_dir=vault_dir,
        password=password,
        version_a=v_a,
        version_b=v_b,
        show_keys=show_keys,
    )


def test_cmd_similarity_requires_two_versions(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    cmd_similarity(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "at least two" in out


def test_cmd_similarity_prints_output(vault_dir, env_file, tmp_path, capsys):
    push(vault_dir, env_file)
    env2 = tmp_path / ".env2"
    env2.write_text("KEY_A=hello\nKEY_C=new\n")
    push(vault_dir, str(env2))
    cmd_similarity(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "similarity" in out.lower() or "Versions" in out


def test_cmd_similarity_invalid_version_a(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    push(vault_dir, env_file)
    cmd_similarity(make_args(vault_dir, v_a=999))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_similarity_invalid_version_b(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    push(vault_dir, env_file)
    cmd_similarity(make_args(vault_dir, v_b=999))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_similarity_show_keys(vault_dir, env_file, tmp_path, capsys):
    push(vault_dir, env_file)
    env2 = tmp_path / ".env2"
    env2.write_text("KEY_A=changed\nKEY_NEW=yes\n")
    push(vault_dir, str(env2))
    cmd_similarity(make_args(vault_dir, show_keys=True))
    out = capsys.readouterr().out
    # With show_keys, changed/added/removed sections should appear
    assert any(marker in out for marker in ["~", "+", "-", "Changed", "Only"])
