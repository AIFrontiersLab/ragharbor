"""Shared fixtures. Every fixture builds isolated, in-memory infrastructure."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from answer_or_abstain_rag.adapters.outbound.memory_corpus import InMemoryCorpus  # noqa: E402
from answer_or_abstain_rag.config.settings import Settings  # noqa: E402
from answer_or_abstain_rag.container import build_container  # noqa: E402
from answer_or_abstain_rag.domain.models import Candidate  # noqa: E402
from answer_or_abstain_rag.kernel.clock import FakeClock  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
def corpus() -> InMemoryCorpus:
    rows = json.loads((FIXTURES / "corpus.json").read_text(encoding="utf-8"))
    return InMemoryCorpus([Candidate.from_dict(r) for r in rows])


@pytest.fixture
def container(settings, clock, corpus):
    return build_container(settings, clock=clock, corpus=corpus)


@pytest.fixture
def services(container):
    return container.services


@pytest.fixture
def make_request():
    def _make(**overrides) -> dict:
        body = {
            "query": "how are retrieval results governed by policy",
            "tenant": "acme",
            "principal": {"subject": "alice", "roles": ["reader"], "groups": ["eng"]},
            "candidates": [
                {"doc_id": "doc-a", "text": "Retrieval results are governed by access policy and clearance.", "score": 0.82, "classification": "internal"},
                {"doc_id": "doc-b", "text": "Quarterly marketing plan and brand voice.", "score": 0.91, "classification": "public"},
                {"doc_id": "doc-c", "text": "Policy enforcement filters retrieval candidates before answering.", "score": 0.64, "classification": "internal"},
                {"doc_id": "doc-d", "text": "Restricted incident report on retrieval policy breach.", "score": 0.77, "classification": "restricted"},
            ],
        }
        body.update(overrides)
        return body

    return _make
