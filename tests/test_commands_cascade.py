"""Tests for envault.commands_cascade."""
import argparse
import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_cascade import cmd_cascade, register


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / ".envault")
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("A=1\nB=2\n")
    return str(p)


def push(vault_dir, env_file, password="secret"):
    args = argparse.Namespace(
        vault_dir=vault_dir,
        env_file=env_file,
        password=password,
        message=None,
    )
    cmd_push(args)


def make_args(vault_dir, versions, password="secret", show_sources=False, output=None):
    return argparse.Namespace(
        vault_dir=vault_dir,
        versions=versions,
        password=password,
        show_sources=show_sources,
        output=output,
    )


def test_cmd_cascade_no_versions_prints_message(vault_dir, capsys):
    args = make_args(vault_dir, ["1"])
    cmd_cascade(args)
    out = capsys.readouterr().out
    assert "No versions" in out


def test_cmd_cascade_single_version(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir, ["1"])
    cmd_cascade(args)
    out = capsys.readouterr().out
    assert "A=1" in out
    assert "B=2" in out


def test_cmd_cascade_two_versions_later_wins(vault_dir, tmp_path, capsys):
    push(vault_dir, env_file=str(tmp_path / ".env"))
    # create first version
    f1 = tmp_path / "v1.env"
    f1.write_text("A=base\nC=shared\n")
    push(vault_dir, env_file=str(f1))
    f2 = tmp_path / "v2.env"
    f2.write_text("A=override\nD=new\n")
    push(vault_dir, env_file=str(f2))
    args = make_args(vault_dir, ["1", "2"])
    cmd_cascade(args)
    out = capsys.readouterr().out
    assert "A=override" in out


def test_cmd_cascade_show_sources(vault_dir, tmp_path, capsys):
    f = tmp_path / "e.env"
    f.write_text("KEY=val\n")
    push(vault_dir, env_file=str(f))
    args = make_args(vault_dir, ["base:1"], show_sources=True)
    cmd_cascade(args)
    out = capsys.readouterr().out
    assert "# source: base" in out


def test_cmd_cascade_output_to_file(vault_dir, tmp_path):
    f = tmp_path / "e.env"
    f.write_text("X=42\n")
    push(vault_dir, env_file=str(f))
    out_file = str(tmp_path / "out.env")
    args = make_args(vault_dir, ["1"], output=out_file)
    cmd_cascade(args)
    content = Path(out_file).read_text()
    assert "X=42" in content


def test_register_adds_cascade_subcommand():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register(subparsers)
    args = parser.parse_args(["cascade", "--password", "pw", "1", "2"])
    assert args.versions == ["1", "2"]
    assert args.password == "pw"
