"""Seeded randomized testing: invariants hold for many generated requests."""

import random

import pytest

from answer_or_abstain_rag.application.commands import RunPipeline
from answer_or_abstain_rag.domain.value_objects import Clearance

WORDS = "policy retrieval evidence ranking budget tenant answer cache audit approval index vector lexical".split()
LEVELS = ["public", "internal", "confidential", "restricted"]
ROLES = ["guest", "reader", "analyst", "admin"]


def _random_request(rng: random.Random) -> dict:
    return {
        "query": " ".join(rng.sample(WORDS, 3)),
        "tenant": rng.choice(["acme", "globex"]),
        "principal": {"subject": "p", "roles": [rng.choice(ROLES)], "groups": rng.sample(["eng", "security", "finance"], 1)},
        "budget_tokens": rng.choice([None, 5, 50, 500]),
        "candidates": [
            {
                "doc_id": f"d{i}",
                "text": " ".join(rng.choices(WORDS, k=rng.randint(0, 12))),
                "score": round(rng.random(), 3),
                "classification": rng.choice(LEVELS),
                "acl": rng.choice([[], ["eng"], ["security"]]),
            }
            for i in range(rng.randint(0, 12))
        ],
    }


@pytest.mark.parametrize("seed", range(40))
def test_invariants(seed, container, settings):
    rng = random.Random(seed)
    body = _random_request(rng)
    result = container.bus.handle(RunPipeline(request=body))
    role = body["principal"]["roles"][0]
    clearance = Clearance.parse(settings.governance.role_clearances[role])
    by_id = {c["doc_id"]: c for c in body["candidates"]}
    if result["answer"]:
        cites = result["answer"]["citations"]
        scores = [c["score"] for c in cites]
        assert scores == sorted(scores, reverse=True)
        assert len({c["doc_id"] for c in cites}) == len(cites)
        for cite in cites:
            source = by_id.get(cite["doc_id"])
            if source is None:
                continue  # retrieved from the corpus
            assert Clearance.parse(source["classification"]) <= clearance
            if source["acl"]:
                assert set(source["acl"]) & set(body["principal"]["groups"])
    else:
        assert result["abstain_reason"]
