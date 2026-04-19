"""CLI commands for notification webhook management."""
from envault.env_notify import set_webhook, remove_webhook, get_webhook, send_notification


def cmd_notify_set(args) -> None:
    set_webhook(args.vault_dir, args.url)
    print(f"Webhook set to: {args.url}")


def cmd_notify_remove(args) -> None:
    remove_webhook(args.vault_dir)
    print("Webhook removed.")


def cmd_notify_show(args) -> None:
    url = get_webhook(args.vault_dir)
    if url:
        print(f"Webhook URL: {url}")
    else:
        print("No webhook configured.")


def cmd_notify_test(args) -> None:
    ok = send_notification(args.vault_dir, "test", {"message": "envault test notification"})
    if ok:
        print("Test notification sent successfully.")
    else:
        url = get_webhook(args.vault_dir)
        if not url:
            print("No webhook configured. Use 'notify set <url>' first.")
        else:
            print("Failed to send notification. Check the webhook URL.")


def register(subparsers, vault_dir_arg) -> None:
    p = subparsers.add_parser("notify", help="Manage webhook notifications")
    sub = p.add_subparsers(dest="notify_cmd")

    ps = sub.add_parser("set", help="Set webhook URL")
    vault_dir_arg(ps)
    ps.add_argument("url", help="Webhook URL")
    ps.set_defaults(func=cmd_notify_set)

    pr = sub.add_parser("remove", help="Remove webhook")
    vault_dir_arg(pr)
    pr.set_defaults(func=cmd_notify_remove)

    psh = sub.add_parser("show", help="Show current webhook")
    vault_dir_arg(psh)
    psh.set_defaults(func=cmd_notify_show)

    pt = sub.add_parser("test", help="Send a test notification")
    vault_dir_arg(pt)
    pt.set_defaults(func=cmd_notify_test)
