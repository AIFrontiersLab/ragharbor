"""Text utilities shared by scoring, redaction, and budgeting."""

from __future__ import annotations

import re

_TOKEN = re.compile(r"[a-z0-9]+")
STOPWORDS = frozenset(
    "a an and are as at be by for from has have in is it its of on or that the to was were will with".split()
)


def normalize(text: str) -> str:
    return " ".join((text or "").split())


def tokenize(text: str, *, drop_stopwords: bool = True) -> list[str]:
    tokens = _TOKEN.findall((text or "").lower())
    if drop_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens


def estimate_tokens(text: str) -> int:
    """Cheap, deterministic token estimate (~4 characters per token)."""
    return max(1, len(text or "") // 4 + 1)


def snippet(text: str, limit: int = 160) -> str:
    clean = normalize(text)
    return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"
