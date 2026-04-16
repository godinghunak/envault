"""CLI command handlers for team sharing: keygen, share, receive."""

import sys
from pathlib import Path
from envault.keystore import init_keystore, load_private_key, load_public_key, public_key_path
from envault.sharing import encrypt_secret_for_recipient, decrypt_secret_from_sender


def cmd_keygen(args) -> None:
    """Generate a local keypair for the current user."""
    ks = init_keystore()
    pub_path = public_key_path()
    print(f"Keypair ready at {ks}")
    print(f"Share your public key with teammates:\n  {pub_path}")


def cmd_share(args) -> None:
    """Encrypt the vault password for a recipient and print the payload.

    Usage: envault share --recipient <pubkey_path> --secret <vault_password>
    """
    recipient_pub_path = Path(args.recipient)
    if not recipient_pub_path.exists():
        print(f"Error: recipient public key not found: {recipient_pub_path}", file=sys.stderr)
        sys.exit(1)
    secret = args.secret.encode() if isinstance(args.secret, str) else args.secret
    recipient_pub = recipient_pub_path.read_bytes()
    payload = encrypt_secret_for_recipient(secret, recipient_pub)
    if args.output:
        Path(args.output).write_text(payload)
        print(f"Encrypted payload written to {args.output}")
    else:
        print(payload)


def cmd_receive(args) -> None:
    """Decrypt a shared vault password using the local private key.

    Usage: envault receive --payload <payload_file_or_string>
    """
    payload_path = Path(args.payload)
    if payload_path.exists():
        payload_json = payload_path.read_text()
    else:
        payload_json = args.payload
    try:
        private_pem = load_private_key()
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    try:
        secret = decrypt_secret_from_sender(payload_json, private_pem)
        print(f"Decrypted vault password: {secret.decode()}")
    except Exception as exc:
        print(f"Decryption failed: {exc}", file=sys.stderr)
        sys.exit(1)
