from envault.templates import add_template, remove_template, list_templates, get_template, render_template
from envault.vault import load_manifest


def cmd_template_add(args):
    keys = args.keys.split(",") if args.keys else []
    add_template(args.vault_dir, args.name, keys)
    print(f"Template '{args.name}' added with keys: {keys}")


def cmd_template_remove(args):
    remove_template(args.vault_dir, args.name)
    print(f"Template '{args.name}' removed.")


def cmd_template_list(args):
    templates = list_templates(args.vault_dir)
    if not templates:
        print("No templates defined.")
    else:
        for name, keys in templates.items():
            print(f"  {name}: {', '.join(keys)}")


def cmd_template_show(args):
    tmpl = get_template(args.vault_dir, args.name)
    if tmpl is None:
        print(f"Template '{args.name}' not found.")
        return
    print(f"Template '{args.name}':")
    for key in tmpl:
        print(f"  {key}")


def cmd_template_render(args):
    manifest = load_manifest(args.vault_dir)
    versions = manifest.get("versions", [])
    if not versions:
        print("No versions available.")
        return
    version = args.version if args.version else versions[-1]["version"]
    rendered = render_template(args.vault_dir, args.name, version, args.password)
    for key, value in rendered.items():
        print(f"{key}={value}")
