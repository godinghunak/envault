"""CLI commands for search feature."""

from envault.search import search_key, search_value, search_in_version


def cmd_search(args):
    """Handle the search command.

    Searches vault entries by key or value pattern. If a version is specified,
    searches only within that specific version. Otherwise, searches across all
    versions using the given mode ('key' or 'value').

    Args:
        args: Parsed CLI arguments containing vault_dir, password, pattern,
              and optionally mode and version.
    """
    vault_dir = args.vault_dir
    password = args.password
    pattern = args.pattern
    mode = getattr(args, "mode", "key")
    version = getattr(args, "version", None)

    if version is not None:
        try:
            results = search_in_version(vault_dir, password, int(version), pattern)
        except ValueError as e:
            print(f"Error: {e}")
            return
        if not results:
            print(f"No keys matching '{pattern}' in version {version}.")
            return
        for key, value in results.items():
            print(f"  {key}={value}")
        return

    if mode == "value":
        results = search_value(vault_dir, password, pattern)
        label = "value"
    else:
        results = search_key(vault_dir, password, pattern)
        label = "key"

    if not results:
        print(f"No matches for {label} pattern '{pattern}'.")
        return

    for match in results:
        print(f"  v{match['version']:>3}  {match['key']}={match['value']}")
