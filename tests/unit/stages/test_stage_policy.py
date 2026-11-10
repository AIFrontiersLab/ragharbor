from answer_or_abstain_rag.domain.models import Candidate, PipelineContext, Request
from answer_or_abstain_rag.stages.policy import PolicyStage


def _ctx(principal, candidates):
    return PipelineContext(run_id="r", request=Request.from_dict({"query": "q", "tenant": "acme", "principal": principal}), candidates=candidates)


def test_filters_by_clearance_and_acl(services):
    ctx = _ctx(
        {"subject": "a", "roles": ["reader"], "groups": ["eng"]},
        [
            Candidate("ok", "fine", classification="internal"),
            Candidate("too-high", "secret", classification="restricted"),
            Candidate("acl", "eng only", classification="internal", acl=("finance",)),
        ],
    )
    PolicyStage("policy", services).process(ctx)
    assert [c.doc_id for c in ctx.candidates] == ["ok"]
    reasons = {d["doc_id"]: d["reason"] for d in ctx.metadata["denied"]}
    assert reasons == {"too-high": "insufficient_clearance", "acl": "acl_denied"}


def test_redacts_pii(services):
    ctx = _ctx({"roles": ["reader"]}, [Candidate("p", "mail jane@example.com or 555-123-4567", classification="public")])
    PolicyStage("policy", services).process(ctx)
    assert "[EMAIL]" in ctx.candidates[0].text
    assert ctx.candidates[0].metadata["redactions"]["email"] == 1
