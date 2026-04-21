"""Tests for envault.commands_namespace module."""
import argparse
import pytest

from envault.vault import init_vault
from envault.env_namespace import add_namespace
from envault.commands_namespace import (
    cmd_namespace_add,
    cmd_namespace_remove,
    cmd_namespace_list,
)


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d)
    return d


def make_args(vault_dir, **kwargs):
    ns = argparse.Namespace(vault_dir=vault_dir, password="secret")
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_cmd_namespace_add_prints_confirmation(vault_dir, capsys):
    args = make_args(vault_dir, name="db", prefix="DB_")
    cmd_namespace_add(args)
    out = capsys.readouterr().out
    assert "db" in out
    assert "DB_" in out


def test_cmd_namespace_add_empty_name_prints_error(vault_dir, capsys):
    args = make_args(vault_dir, name="", prefix="DB_")
    cmd_namespace_add(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_namespace_remove_prints_confirmation(vault_dir, capsys):
    add_namespace(vault_dir, "cache", "CACHE_")
    args = make_args(vault_dir, name="cache")
    cmd_namespace_remove(args)
    out = capsys.readouterr().out
    assert "cache" in out


def test_cmd_namespace_remove_missing_prints_error(vault_dir, capsys):
    args = make_args(vault_dir, name="ghost")
    cmd_namespace_remove(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_namespace_list_empty(vault_dir, capsys):
    args = make_args(vault_dir)
    cmd_namespace_list(args)
    out = capsys.readouterr().out
    assert "No namespaces" in out


def test_cmd_namespace_list_shows_entries(vault_dir, capsys):
    add_namespace(vault_dir, "db", "DB_")
    add_namespace(vault_dir, "aws", "AWS_")
    args = make_args(vault_dir)
    cmd_namespace_list(args)
    out = capsys.readouterr().out
    assert "db" in out
    assert "aws" in out
    assert "DB_" in out
    assert "AWS_" in out
