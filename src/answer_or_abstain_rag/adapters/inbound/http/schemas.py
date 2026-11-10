"""Request parsing and response envelopes for the HTTP adapter."""

from __future__ import annotations

import json

from answer_or_abstain_rag.kernel.errors import ValidationError

MAX_BODY_BYTES = 1_000_000


def read_json(environ: dict) -> dict:
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError as exc:
        raise ValidationError("invalid Content-Length") from exc
    if length > MAX_BODY_BYTES:
        raise ValidationError("request body too large", details={"limit": MAX_BODY_BYTES})
    raw = environ["wsgi.input"].read(length) if length else b""
    if not raw:
        raise ValidationError("request body is required")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError("request body must be valid JSON") from exc
    if not isinstance(data, dict):
        raise ValidationError("request body must be a JSON object")
    return data


def envelope(data, *, request_id: str) -> dict:
    return {"data": data, "request_id": request_id}
