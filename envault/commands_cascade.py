"""CLI commands for env cascade (priority-ordered merge of multiple versions)."""
import argparse
from envault.vault import init_vault, load_manifest
from envault.env_cascade import cascade_versions, format_cascade


def cmd_cascade(args: argparse.Namespace) -> None:
    vault_dir = args.vault_dir
    password = args.password
    show_sources = getattr(args, "show_sources", False)
    output_file = getattr(args, "output", None)

    manifest = load_manifest(vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        print("No versions found in vault.")
        return

    # Parse version specs: "base:1,override:2" or just "1,2"
    raw_specs = args.versions  # e.g. ["1", "2"] or ["base:1", "prod:2"]
    version_labels = []
    for spec in raw_specs:
        if ":" in spec:
            label, ver = spec.split(":", 1)
            version_labels.append((label.strip(), int(ver.strip())))
        else:
            ver = int(spec.strip())
            version_labels.append((f"v{ver}", ver))

    try:
        result = cascade_versions(vault_dir, password, version_labels)
    except Exception as e:
        print(f"Error during cascade: {e}")
        return

    formatted = format_cascade(result, show_sources=show_sources)

    if output_file:
        with open(output_file, "w") as f:
            f.write(formatted + "\n")
        print(f"Cascaded env written to {output_file} ({len(result.merged)} keys).")
    else:
        print(formatted)


def register(subparsers) -> None:
    p = subparsers.add_parser(
        "cascade",
        help="Merge multiple vault versions in priority order (last wins).",
    )
    p.add_argument(
        "versions",
        nargs="+",
        metavar="[LABEL:]VERSION",
        help="Versions to cascade, e.g. 1 2 or base:1 prod:2",
    )
    p.add_argument("--vault-dir", default=".envault", help="Vault directory")
    p.add_argument("--password", required=True, help="Decryption password")
    p.add_argument("--show-sources", action="store_true", help="Annotate each key with its source layer")
    p.add_argument("--output", metavar="FILE", help="Write result to file instead of stdout")
    p.set_defaults(func=cmd_cascade)
