"""Tests for envault.commands_completion."""
import sys
import types
import pytest

from envault.commands_completion import (
    cmd_completion_generate,
    cmd_completion_install,
    cmd_completion_shells,
)
from envault.env_completion import SUPPORTED_SHELLS


def make_args(**kwargs):
    ns = types.SimpleNamespace(**kwargs)
    return ns


def test_cmd_completion_generate_bash(capsys):
    args = make_args(shell="bash")
    cmd_completion_generate(args)
    out = capsys.readouterr().out
    assert "_envault_completions" in out


def test_cmd_completion_generate_zsh(capsys):
    args = make_args(shell="zsh")
    cmd_completion_generate(args)
    out = capsys.readouterr().out
    assert "#compdef envault" in out


def test_cmd_completion_generate_fish(capsys):
    args = make_args(shell="fish")
    cmd_completion_generate(args)
    out = capsys.readouterr().out
    assert "complete -c envault" in out


def test_cmd_completion_generate_bad_shell_exits(capsys):
    args = make_args(shell="powershell")
    with pytest.raises(SystemExit):
        cmd_completion_generate(args)
    err = capsys.readouterr().err
    assert "Unsupported shell" in err


def test_cmd_completion_install_creates_file(tmp_path, capsys):
    dest = str(tmp_path / "envault.bash")
    args = make_args(shell="bash", output=dest)
    cmd_completion_install(args)
    out = capsys.readouterr().out
    assert dest in out
    import os
    assert os.path.isfile(dest)


def test_cmd_completion_install_bad_shell_exits(tmp_path, capsys):
    dest = str(tmp_path / "envault.ps1")
    args = make_args(shell="powershell", output=dest)
    with pytest.raises(SystemExit):
        cmd_completion_install(args)


def test_cmd_completion_shells_lists_all(capsys):
    cmd_completion_shells(make_args())
    out = capsys.readouterr().out
    for shell in SUPPORTED_SHELLS:
        assert shell in out
