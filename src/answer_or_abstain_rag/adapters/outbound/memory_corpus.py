"""In-memory document corpus with lexical search, used when callers send no candidates."""

from __future__ import annotations

import json
from pathlib import Path

from answer_or_abstain_rag.domain.models import Candidate
from answer_or_abstain_rag.kernel.text import tokenize


class InMemoryCorpus:
    def __init__(self, documents: list[Candidate] | None = None) -> None:
        self._docs: dict[str, Candidate] = {}
        for doc in documents or []:
            self.upsert(doc)

    @classmethod
    def from_json(cls, path: str | Path) -> "InMemoryCorpus":
        rows = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls([Candidate.from_dict(r) for r in rows])

    def upsert(self, candidate: Candidate) -> None:
        self._docs[candidate.doc_id] = candidate

    def search(self, query: str, *, tenant: str, limit: int) -> list[Candidate]:
        terms = set(tokenize(query))
        scored = []
        for doc in self._docs.values():
            owner = doc.metadata.get("tenant")
            if owner is not None and owner != tenant:
                continue
            overlap = len(terms & set(tokenize(doc.text)))
            if overlap:
                scored.append((overlap / max(1, len(terms)), doc))
        scored.sort(key=lambda item: (-item[0], item[1].doc_id))
        out = []
        for score, doc in scored[:limit]:
            out.append(
                Candidate(
                    doc_id=doc.doc_id,
                    text=doc.text,
                    prior_score=round(score, 6),
                    score=round(score, 6),
                    classification=doc.classification,
                    acl=doc.acl,
                    metadata=dict(doc.metadata),
                )
            )
        return out

    def __len__(self) -> int:
        return len(self._docs)
