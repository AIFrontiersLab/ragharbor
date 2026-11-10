import pytest

from answer_or_abstain_rag.domain.models import Answer, Candidate, Citation, Request
from answer_or_abstain_rag.kernel.errors import ValidationError


def test_request_from_dict_parses_nested_fields():
    req = Request.from_dict(
        {
            "query": "  policy  ",
            "tenant": "acme",
            "principal": {"subject": "alice", "roles": ["analyst"], "groups": ["eng"]},
            "candidates": [{"doc_id": "d1", "score": 0.4, "acl": ["eng"]}],
        }
    )
    assert req.query == "policy"
    assert req.principal.tenant == "acme"
    assert req.candidates[0].prior_score == 0.4
    assert req.candidates[0].acl == ("eng",)


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"query": ""},
        {"query": "x" * 5000},
        {"query": "q", "candidates": "nope"},
        {"query": "q", "candidates": [{"text": "missing id"}]},
        {"query": "q", "budget_tokens": -1},
        {"query": "q", "top_k": 0},
    ],
)
def test_invalid_requests_raise(body):
    with pytest.raises(ValidationError):
        Request.from_dict(body)


def test_answer_evidence_ids_follow_citations():
    answer = Answer("t", [Citation("a", 0.9), Citation("b", 0.5)])
    assert answer.evidence_ids == ["a", "b"]
    assert answer.to_dict()["citations"][0]["doc_id"] == "a"


def test_candidate_round_trip():
    cand = Candidate.from_dict({"doc_id": "d", "acl": ["x"], "classification": "PUBLIC"})
    assert cand.classification == "public"
    assert cand.to_dict()["acl"] == ["x"]
