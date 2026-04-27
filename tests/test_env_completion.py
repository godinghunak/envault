"""Tests for envault.env_completion."""
import os
import pytest

from envault.env_completion import (
    BANNER,
    SUPPORTED_SHELLS,
    CompletionError,
    generate_bash,
    generate_zsh,
    generate_fish,
    generate_completion,
    write_completion_file,
)

COMMANDS = ["init", "push", "pull", "list"]


def test_supported_shells_includes_bash_zsh_fish():
    assert "bash" in SUPPORTED_SHELLS
    assert "zsh" in SUPPORTED_SHELLS
    assert "fish" in SUPPORTED_SHELLS


def test_generate_bash_contains_banner():
    script = generate_bash(COMMANDS)
    assert BANNER in script


def test_generate_bash_contains_commands():
    script = generate_bash(COMMANDS)
    for cmd in COMMANDS:
        assert cmd in script


def test_generate_bash_has_complete_directive():
    script = generate_bash(COMMANDS)
    assert "complete -F _envault_completions envault" in script


def test_generate_zsh_contains_banner():
    script = generate_zsh(COMMANDS)
    assert BANNER in script


def test_generate_zsh_contains_commands():
    script = generate_zsh(COMMANDS)
    for cmd in COMMANDS:
        assert cmd in script


def test_generate_zsh_has_compdef():
    script = generate_zsh(COMMANDS)
    assert "#compdef envault" in script


def test_generate_fish_contains_banner():
    script = generate_fish(COMMANDS)
    assert BANNER in script


def test_generate_fish_contains_commands():
    script = generate_fish(COMMANDS)
    for cmd in COMMANDS:
        assert cmd in script


def test_generate_completion_bash():
    script = generate_completion("bash", COMMANDS)
    assert "_envault_completions" in script


def test_generate_completion_case_insensitive():
    script = generate_completion("BASH", COMMANDS)
    assert "_envault_completions" in script


def test_generate_completion_unsupported_shell_raises():
    with pytest.raises(CompletionError, match="Unsupported shell"):
        generate_completion("powershell", COMMANDS)


def test_write_completion_file_creates_file(tmp_path):
    dest = str(tmp_path / "completions" / "envault.bash")
    result = write_completion_file("bash", COMMANDS, dest)
    assert os.path.isfile(result)


def test_write_completion_file_content_is_valid(tmp_path):
    dest = str(tmp_path / "envault.zsh")
    write_completion_file("zsh", COMMANDS, dest)
    with open(dest) as fh:
        content = fh.read()
    assert "#compdef envault" in content


def test_write_completion_file_returns_path(tmp_path):
    dest = str(tmp_path / "envault.fish")
    returned = write_completion_file("fish", COMMANDS, dest)
    assert returned == dest
