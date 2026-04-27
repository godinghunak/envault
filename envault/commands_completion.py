"""CLI commands for shell completion management."""
from __future__ import annotations

import sys

from envault.env_completion import (
    SUPPORTED_SHELLS,
    CompletionError,
    generate_completion,
    write_completion_file,
)

_DEFAULT_COMMANDS = [
    "init", "push", "pull", "list", "diff", "log", "rollback", "versions",
    "export", "tag", "hook", "profile", "template", "search", "lint",
    "import", "compare", "lock", "watch", "rename", "keys", "merge",
    "redact", "rotate", "annotate", "clone", "snapshot", "alias",
    "archive", "blame", "sign", "verify", "format", "decrypt", "summary",
    "policy", "expire", "backup", "restore", "quota", "access", "health",
    "notify", "prune", "stats", "patch", "filter", "reorder", "placeholder",
    "deps", "copy", "trim", "mask", "dedupe", "validate", "group", "split",
    "namespace", "report", "completion",
]


def cmd_completion_generate(args) -> None:
    """Print a shell completion script to stdout."""
    shell = args.shell
    try:
        script = generate_completion(shell, _DEFAULT_COMMANDS)
    except CompletionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(script, end="")


def cmd_completion_install(args) -> None:
    """Write a completion script to a file."""
    shell = args.shell
    path = args.output
    try:
        dest = write_completion_file(shell, _DEFAULT_COMMANDS, path)
    except CompletionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Completion script written to: {dest}")


def cmd_completion_shells(_args) -> None:
    """List supported shells."""
    for shell in SUPPORTED_SHELLS:
        print(shell)


def register(subparsers) -> None:
    p = subparsers.add_parser("completion", help="Shell completion helpers")
    sub = p.add_subparsers(dest="completion_cmd")

    gen = sub.add_parser("generate", help="Print completion script")
    gen.add_argument("shell", choices=SUPPORTED_SHELLS)
    gen.set_defaults(func=cmd_completion_generate)

    inst = sub.add_parser("install", help="Write completion script to a file")
    inst.add_argument("shell", choices=SUPPORTED_SHELLS)
    inst.add_argument("output", help="Destination file path")
    inst.set_defaults(func=cmd_completion_install)

    shells = sub.add_parser("shells", help="List supported shells")
    shells.set_defaults(func=cmd_completion_shells)
