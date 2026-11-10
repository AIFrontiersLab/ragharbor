from answer_or_abstain_rag.domain.models import Candidate, PipelineContext, Request
from answer_or_abstain_rag.stages.fallback import FallbackStage


def _ctx():
    return PipelineContext(
        run_id="r",
        request=Request.from_dict({"query": "q"}),
        candidates=[Candidate("low", prior_score=0.1, score=0.9), Candidate("high", prior_score=0.8, score=0.2)],
    )


def test_noop_when_healthy(services):
    ctx = _ctx()
    FallbackStage("fb", services).process(ctx)
    assert ctx.candidates[0].doc_id == "low"


def test_restores_prior_order_when_degraded(services):
    ctx = _ctx()
    ctx.degraded = True
    ctx.errors.append({"stage": "score"})
    FallbackStage("fb", services).process(ctx)
    assert [c.doc_id for c in ctx.candidates] == ["high", "low"]
    assert ctx.decisions[-1]["failed_stages"] == ["score"]
