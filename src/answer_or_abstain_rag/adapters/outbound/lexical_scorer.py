"""Deterministic BM25-style relevance scorer normalised into [0, 1].

This is the reference scorer. Swap in a learned model by implementing
``RelevanceScorer`` and registering it in ``container.py``; nothing else changes.
"""

from __future__ import annotations

import math
from collections import Counter

from answer_or_abstain_rag.domain.models import Candidate
from answer_or_abstain_rag.kernel.text import tokenize


class LexicalScorer:
    name = "lexical-bm25"

    def __init__(self, k1: float = 1.2, b: float = 0.75, avg_doc_len: float = 60.0) -> None:
        self.k1 = k1
        self.b = b
        self.avg_doc_len = avg_doc_len

    def score(self, query: str, candidate: Candidate) -> float:
        q_terms = tokenize(query)
        d_terms = tokenize(candidate.text)
        if not q_terms or not d_terms:
            return 0.0
        tf = Counter(d_terms)
        length_norm = 1 - self.b + self.b * (len(d_terms) / self.avg_doc_len)
        raw = 0.0
        for term in set(q_terms):
            f = tf.get(term, 0)
            if f:
                raw += (f * (self.k1 + 1)) / (f + self.k1 * length_norm)
        best = len(set(q_terms)) * (self.k1 + 1)
        return round(min(1.0, raw / best) if best else 0.0, 6) if not math.isnan(raw) else 0.0
