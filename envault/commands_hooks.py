import argparse
from envault import hooks


def cmd_hook_install(args):
    """Install a hook into the vault's hooks directory."""
    try:
        hooks.install_hook(args.vault_dir, args.hook_name, args.script)
        print(f"Hook '{args.hook_name}' installed successfully.")
    except ValueError as e:
        print(f"Error: {e}")
        raise SystemExit(1)
    except OSError as e:
        print(f"Failed to install hook: {e}")
        raise SystemExit(1)


def cmd_hook_remove(args):
    """Remove an installed hook."""
    try:
        hooks.remove_hook(args.vault_dir, args.hook_name)
        print(f"Hook '{args.hook_name}' removed.")
    except FileNotFoundError:
        print(f"Hook '{args.hook_name}' is not installed.")
        raise SystemExit(1)


def cmd_hook_list(args):
    """List all installed hooks."""
    installed = hooks.list_hooks(args.vault_dir)
    if not installed:
        print("No hooks installed.")
    else:
        print("Installed hooks:")
        for name in installed:
            print(f"  {name}")


def cmd_hook_run(args):
    """Manually run a hook by name."""
    try:
        hooks.run_hook(args.vault_dir, args.hook_name)
    except FileNotFoundError:
        print(f"Hook '{args.hook_name}' is not installed.")
        raise SystemExit(1)
    except Exception as e:
        print(f"Hook '{args.hook_name}' failed: {e}")
        raise SystemExit(1)
