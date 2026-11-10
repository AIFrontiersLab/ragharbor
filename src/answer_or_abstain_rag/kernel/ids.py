"""Identifier helpers: random ids for runs, stable hashes for cache keys."""

from __future__ import annotations

import hashlib
import json
import uuid


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def stable_hash(payload: object, *, length: int = 24) -> str:
    """Deterministic content hash for any JSON-serialisable payload."""
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:length]
