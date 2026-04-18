import pytest
import stat
from pathlib import Path
from argparse import Namespace
from unittest.mock import patch, MagicMock
from envault import hooks
from envault.commands_hooks import (
    cmd_hook_install,
    cmd_hook_remove,
    cmd_hook_list,
    cmd_hook_run,
)


@pytest.fixture
def vault_dir(tmp_path):
    hooks.init_hooks(tmp_path)
    return tmp_path


def make_args(**kwargs):
    return Namespace(**kwargs)


def test_cmd_hook_list_empty(vault_dir, capsys):
    args = make_args(vault_dir=vault_dir)
    cmd_hook_list(args)
    out = capsys.readouterr().out
    assert "No hooks installed" in out


def test_cmd_hook_install_and_list(vault_dir, capsys):
    script = "#!/bin/sh\necho pushed"
    args = make_args(vault_dir=vault_dir, hook_name="post-push", script=script)
    cmd_hook_install(args)
    out = capsys.readouterr().out
    assert "installed" in out

    list_args = make_args(vault_dir=vault_dir)
    cmd_hook_list(list_args)
    out = capsys.readouterr().out
    assert "post-push" in out


def test_cmd_hook_install_invalid_name(vault_dir):
    args = make_args(vault_dir=vault_dir, hook_name="invalid-hook", script="echo hi")
    with pytest.raises(SystemExit):
        cmd_hook_install(args)


def test_cmd_hook_remove(vault_dir, capsys):
    script = "#!/bin/sh\necho hi"
    hooks.install_hook(vault_dir, "post-push", script)
    args = make_args(vault_dir=vault_dir, hook_name="post-push")
    cmd_hook_remove(args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_hook_remove_not_installed(vault_dir):
    args = make_args(vault_dir=vault_dir, hook_name="post-push")
    with pytest.raises(SystemExit):
        cmd_hook_remove(args)


def test_cmd_hook_run_not_installed(vault_dir):
    args = make_args(vault_dir=vault_dir, hook_name="post-push")
    with pytest.raises(SystemExit):
        cmd_hook_run(args)
