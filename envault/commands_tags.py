"""CLI commands for managing version tags."""

from envault.tags import add_tag, remove_tag, list_tags, resolve_tag
from envault.vault import load_manifest


def cmd_tag_add(args):
    manifest = load_manifest(args.vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        print("No versions available to tag.")
        return

    version = args.version if args.version is not None else len(versions)
    nums = [v["version"] for v in versions]
    if version not in nums:
        print(f"Version {version} does not exist.")
        return

    add_tag(args.vault_dir, args.tag, version)
    print(f"Tagged version {version} as '{args.tag}'.")


def cmd_tag_remove(args):
    try:
        remove_tag(args.vault_dir, args.tag)
        print(f"Removed tag '{args.tag}'.")
    except KeyError as e:
        print(str(e))


def cmd_tag_list(args):
    tags = list_tags(args.vault_dir)
    if not tags:
        print("No tags defined.")
        return
    print(f"{'Tag':<20} {'Version'}")
    print("-" * 30)
    for tag, version in tags:
        print(f"{tag:<20} {version}")


def cmd_tag_resolve(args):
    try:
        version = resolve_tag(args.vault_dir, args.tag)
        print(f"Tag '{args.tag}' -> version {version}")
    except KeyError as e:
        print(str(e))
