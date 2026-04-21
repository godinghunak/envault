"""CLI commands for heredoc detection and expansion."""

import argparse
from envault.env_heredoc import find_heredocs, validate_heredocs, expand_heredocs
from envault.vault import load_manifest
from envault.export import export_version, export_latest


def _load_text(vault_dir: str, version: int | None) -> str:
    from envault.export import export_latest, export_version
    if version is None:
        return export_latest(vault_dir, password="")
    return export_version(vault_dir, version, password="")


def cmd_heredoc_check(args: argparse.Namespace) -> None:
    """Report unclosed or malformed heredoc blocks in a vault version."""
    try:
        text = _load_text(args.vault_dir, getattr(args, "version", None))
    except Exception as exc:
        print(f"Error loading version: {exc}")
        return

    issues = validate_heredocs(text)
    if not issues:
        print("No heredoc issues found.")
    else:
        for issue in issues:
            print(str(issue))


def cmd_heredoc_list(args: argparse.Namespace) -> None:
    """List all heredoc keys found in a vault version."""
    try:
        text = _load_text(args.vault_dir, getattr(args, "version", None))
    except Exception as exc:
        print(f"Error loading version: {exc}")
        return

    pairs = find_heredocs(text)
    if not pairs:
        print("No heredoc blocks found.")
    else:
        for key, value in pairs:
            lines = value.count("\n") + 1 if value else 0
            print(f"{key}: {lines} line(s)")


def cmd_heredoc_expand(args: argparse.Namespace) -> None:
    """Print expanded heredoc values as KEY=VALUE pairs."""
    try:
        text = _load_text(args.vault_dir, getattr(args, "version", None))
    except Exception as exc:
        print(f"Error loading version: {exc}")
        return

    expanded = expand_heredocs(text)
    if not expanded:
        print("No heredoc blocks to expand.")
    else:
        for key, value in expanded.items():
            escaped = value.replace("\n", "\\n")
            print(f"{key}={escaped}")


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("heredoc", help="Heredoc multiline value tools")
    sub = p.add_subparsers(dest="heredoc_cmd", required=True)

    for name, func, help_text in [
        ("check", cmd_heredoc_check, "Validate heredoc blocks"),
        ("list", cmd_heredoc_list, "List heredoc keys"),
        ("expand", cmd_heredoc_expand, "Expand heredoc values"),
    ]:
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument("--vault-dir", default=".envault")
        sp.add_argument("--version", type=int, default=None)
        sp.set_defaults(func=func)
