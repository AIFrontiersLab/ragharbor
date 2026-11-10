"""``python -m answer_or_abstain_rag`` command-line interface."""

from __future__ import annotations

import argparse
import json
import sys

from answer_or_abstain_rag.adapters.inbound.cli import commands


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="answer_or_abstain_rag", description="Answer-or-Abstain RAG reference service")
    parser.add_argument("--config", help="path to a TOML settings profile")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="execute one request from a JSON file or stdin")
    run.add_argument("request", nargs="?", default="-", help="path to request JSON, or '-' for stdin")
    run.add_argument("--corpus", help="optional JSON corpus to search when no candidates are supplied")

    serve = sub.add_parser("serve", help="start the HTTP server")
    serve.add_argument("--host")
    serve.add_argument("--port", type=int)

    sub.add_parser("describe", help="print the stage topology")
    sub.add_parser("config", help="print effective configuration")
    sub.add_parser("doctor", help="run readiness checks")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler = getattr(commands, f"cmd_{args.command}")
    try:
        result = handler(args)
    except Exception as exc:  # noqa: BLE001 - CLI reports errors as JSON
        payload = exc.to_dict() if hasattr(exc, "to_dict") else {"code": "error", "message": str(exc)}
        print(json.dumps({"error": payload}, indent=2), file=sys.stderr)
        return 2
    if result is not None:
        print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
