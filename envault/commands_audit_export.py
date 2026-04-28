"""CLI command: envault audit-export — export the audit log to a file or stdout."""

from __future__ import annotations

import sys

from envault.env_audit_export import SUPPORTED_FORMATS, export_audit


def cmd_audit_export(args) -> None:
    """Export the audit log in the requested format."""
    vault_dir = getattr(args, "vault_dir", ".envault")
    fmt = getattr(args, "format", "text") or "text"
    limit = getattr(args, "limit", None)
    output = getattr(args, "output", None)

    if fmt not in SUPPORTED_FORMATS:
        print(
            f"Error: unsupported format '{fmt}'. "
            f"Choose from: {', '.join(SUPPORTED_FORMATS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        content = export_audit(vault_dir, fmt=fmt, limit=limit)
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if output:
        try:
            with open(output, "w", encoding="utf-8") as fh:
                fh.write(content)
            print(f"Audit log exported to {output} ({fmt}).")
        except OSError as exc:
            print(f"Error writing file: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(content)


def register(subparsers) -> None:
    """Attach the audit-export sub-command to *subparsers*."""
    p = subparsers.add_parser(
        "audit-export",
        help="Export the audit log to JSON, CSV, or plain text.",
    )
    p.add_argument(
        "--format",
        choices=SUPPORTED_FORMATS,
        default="text",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Export only the last N events.",
    )
    p.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    p.set_defaults(func=cmd_audit_export)
