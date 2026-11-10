"""Pattern-based PII detection. Deliberately conservative: prefer false positives."""

from __future__ import annotations

import re

PATTERNS: dict[str, re.Pattern] = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"\+?\d[\d\s().-]{8,}\d"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
}

DETECTION_ORDER = ("ssn", "credit_card", "email", "phone")


def detect(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for kind in DETECTION_ORDER:
        for match in PATTERNS[kind].finditer(text or ""):
            found.append((kind, match.group(0)))
    return found
