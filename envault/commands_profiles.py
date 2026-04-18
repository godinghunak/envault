"""CLI commands for profile management."""
from envault.profiles import add_profile, remove_profile, list_profiles, get_profile
from envault.vault import init_vault


def cmd_profile_add(args):
    init_vault(args.vault_dir)
    add_profile(args.vault_dir, args.name, args.env_file)
    print(f"Profile '{args.name}' added (env_file={args.env_file}).")


def cmd_profile_remove(args):
    try:
        remove_profile(args.vault_dir, args.name)
        print(f"Profile '{args.name}' removed.")
    except KeyError as e:
        print(str(e))


def cmd_profile_list(args):
    profiles = list_profiles(args.vault_dir)
    if not profiles:
        print("No profiles defined.")
    else:
        for name in profiles:
            info = get_profile(args.vault_dir, name)
            print(f"  {name}: env_file={info['env_file']}")


def cmd_profile_show(args):
    try:
        info = get_profile(args.vault_dir, args.name)
        print(f"Profile: {args.name}")
        for k, v in info.items():
            print(f"  {k}: {v}")
    except KeyError as e:
        print(str(e))
