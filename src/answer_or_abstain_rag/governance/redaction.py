"""Replace detected PII with typed placeholders."""

from __future__ import annotations

from answer_or_abstain_rag.governance.pii import DETECTION_ORDER, PATTERNS


class Redactor:
    def __init__(self, kinds: tuple[str, ...] = DETECTION_ORDER) -> None:
        self.kinds = kinds

    def redact(self, text: str) -> tuple[str, dict[str, int]]:
        hits: dict[str, int] = {}
        out = text or ""
        for kind in self.kinds:
            out, count = PATTERNS[kind].subn(f"[{kind.upper()}]", out)
            if count:
                hits[kind] = count
        return out, hits
