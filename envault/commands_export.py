"""CLI commands for exporting decrypted .env versions."""
import sys
from envault.export import export_version, export_latest, export_to_file
from envault.audit import log_event


def cmd_export(args):
    """Export a decrypted .env version to stdout or a file."""
    vault_dir = args.vault_dir
    password = args.password
    version = getattr(args, "version", None)
    output = getattr(args, "output", None)

    try:
        if version is not None:
            if output:
                export_to_file(vault_dir, version, password, output)
                print(f"Exported version {version} to {output}")
                log_event(vault_dir, "export", {"version": version, "output": output})
            else:
                content = export_version(vault_dir, version, password)
                sys.stdout.write(content)
                log_event(vault_dir, "export", {"version": version, "output": "stdout"})
        else:
            if output:
                from envault.vault import load_manifest
                manifest = load_manifest(vault_dir)
                versions = manifest.get("versions", [])
                if not versions:
                    print("No versions found.")
                    return
                latest = max(versions, key=lambda v: v["version"])["version"]
                export_to_file(vault_dir, latest, password, output)
                print(f"Exported latest (v{latest}) to {output}")
                log_event(vault_dir, "export", {"version": latest, "output": output})
            else:
                content = export_latest(vault_dir, password)
                sys.stdout.write(content)
                log_event(vault_dir, "export", {"version": "latest", "output": "stdout"})
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Decryption failed: {e}", file=sys.stderr)
        sys.exit(1)
