from answer_or_abstain_rag.domain.models import Candidate, PipelineContext, Request
from answer_or_abstain_rag.stages.answer import AnswerStage


def _ctx(cands, **req):
    return PipelineContext(run_id="r", request=Request.from_dict({"query": "q", **req}), candidates=cands)


def test_cites_top_k_in_score_order(services):
    ctx = _ctx([Candidate("a", score=0.2), Candidate("b", score=0.9), Candidate("c", score=0.5)], top_k=2)
    AnswerStage("answer", services).process(ctx)
    assert ctx.answer.evidence_ids == ["b", "c"]


def test_abstains_without_evidence(services):
    ctx = _ctx([])
    AnswerStage("answer", services).process(ctx)
    assert ctx.answer is None and ctx.abstain_reason == "insufficient_evidence"


def test_unverified_answer_when_evidence_not_required(services):
    ctx = _ctx([], require_evidence=False)
    AnswerStage("answer", services).process(ctx)
    assert ctx.answer is not None and ctx.answer.citations == []
