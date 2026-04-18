"""CLI commands for linting .env files."""
from __future__ import annotations
import sys
from envault.lint import lint_env
from envault.vault import load_manifest
from envault.export import export_version, export_latest


def cmd_lint(args) -> None:
    vault_dir = args.vault_dir
    version = getattr(args, "version", None)
    file_path = getattr(args, "file", None)

    if file_path:
        try:
            content = open(file_path).read()
        except FileNotFoundError:
            print(f"File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        source = file_path
    elif version is not None:
        manifest = load_manifest(vault_dir)
        versions = manifest.get("versions", [])
        if version < 1 or version > len(versions):
            print(f"Version {version} does not exist.", file=sys.stderr)
            sys.exit(1)
        content = export_version(vault_dir, version, args.password)
        source = f"version {version}"
    else:
        try:
            content = export_latest(vault_dir, args.password)
            manifest = load_manifest(vault_dir)
            source = f"version {len(manifest.get('versions', []))}"
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    issues = lint_env(content)
    if not issues:
        print(f"No issues found in {source}.")
    else:
        print(f"{len(issues)} issue(s) found in {source}:")
        for issue in issues:
            print(f"  {issue}")
        if any(i.code.startswith("E") for i in issues):
            sys.exit(2)
