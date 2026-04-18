"""Tests for envault/hooks.py"""
import pytest
from envault.hooks import (
    init_hooks, install_hook, remove_hook, run_hook,
    list_hooks, hook_path, HOOK_PRE_PUSH, HOOK_POST_PUSH,
)


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    d.mkdir()
    init_hooks(str(d))
    return str(d)


def test_init_hooks_creates_directory(tmp_path):
    d = tmp_path / ".envault"
    d.mkdir()
    init_hooks(str(d))
    assert (d / "hooks").is_dir()


def test_install_hook_creates_file(vault_dir):
    install_hook(vault_dir, HOOK_PRE_PUSH, "#!/bin/sh\necho hello\n")
    p = hook_path(vault_dir, HOOK_PRE_PUSH)
    assert p.exists()
    assert "echo hello" in p.read_text()


def test_install_hook_is_executable(vault_dir):
    install_hook(vault_dir, HOOK_PRE_PUSH, "#!/bin/sh\nexit 0\n")
    p = hook_path(vault_dir, HOOK_PRE_PUSH)
    assert p.stat().st_mode & 0o111


def test_install_unknown_hook_raises(vault_dir):
    with pytest.raises(ValueError):
        install_hook(vault_dir, "unknown-hook", "#!/bin/sh\n")


def test_remove_hook_returns_true_if_existed(vault_dir):
    install_hook(vault_dir, HOOK_POST_PUSH, "#!/bin/sh\nexit 0\n")
    assert remove_hook(vault_dir, HOOK_POST_PUSH) is True
    assert not hook_path(vault_dir, HOOK_POST_PUSH).exists()


def test_remove_hook_returns_false_if_missing(vault_dir):
    assert remove_hook(vault_dir, HOOK_PRE_PUSH) is False


def test_run_hook_no_hook_returns_zero(vault_dir):
    assert run_hook(vault_dir, HOOK_PRE_PUSH) == 0


def test_run_hook_success(vault_dir):
    install_hook(vault_dir, HOOK_PRE_PUSH, "#!/bin/sh\nexit 0\n")
    assert run_hook(vault_dir, HOOK_PRE_PUSH) == 0


def test_run_hook_failure(vault_dir):
    install_hook(vault_dir, HOOK_PRE_PUSH, "#!/bin/sh\nexit 1\n")
    assert run_hook(vault_dir, HOOK_PRE_PUSH) == 1


def test_list_hooks_empty(vault_dir):
    assert list_hooks(vault_dir) == []


def test_list_hooks_after_install(vault_dir):
    install_hook(vault_dir, HOOK_PRE_PUSH, "#!/bin/sh\nexit 0\n")
    install_hook(vault_dir, HOOK_POST_PUSH, "#!/bin/sh\nexit 0\n")
    hooks = list_hooks(vault_dir)
    assert set(hooks) == {HOOK_PRE_PUSH, HOOK_POST_PUSH}
