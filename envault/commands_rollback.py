"""CLI command handlers for rollback feature."""

import os
from envault.rollback import rollback, list_versions


def cmd_rollback(args):
    """Restore a specific version of an env file."""
    vault_dir = args.vault_dir
    env_name = args.name
    target_version = args.version
    output = args.output or f".env.rollback.v{target_version}"
    password = args.password

    try:
        rollback(vault_dir, env_name, target_version, password, output)
        print(f"Restored '{env_name}' version {target_version} -> {output}")
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        raise SystemExit(1)


def cmd_versions(args):
    """List all stored versions for an env file."""
    vault_dir = args.vault_dir
    env_name = args.name

    versions = list_versions(vault_dir, env_name)
    if not versions:
        print(f"No versions found for '{env_name}'.")
        return

    print(f"Versions for '{env_name}':")
    for v in versions:
        ts = v.get("timestamp", "unknown")
        print(f"  v{v['version']}  ({ts})  file={v['file']}")
