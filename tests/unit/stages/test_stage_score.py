from answer_or_abstain_rag.domain.models import Candidate, PipelineContext, Request
from answer_or_abstain_rag.stages.score import ScoreStage


def test_relevance_can_overturn_prior(services):
    ctx = PipelineContext(
        run_id="r",
        request=Request.from_dict({"query": "policy enforcement retrieval"}),
        candidates=[
            Candidate("noise", "marketing brand voice", prior_score=0.9),
            Candidate("signal", "policy enforcement for retrieval", prior_score=0.6),
        ],
    )
    ScoreStage("score", services).process(ctx)
    assert ctx.candidates[0].doc_id == "signal"
    assert all(0.0 <= c.score <= 1.0 for c in ctx.candidates)


def test_skips_on_cache_hit(services):
    ctx = PipelineContext(run_id="r", request=Request.from_dict({"query": "q"}), candidates=[Candidate("a", "t", prior_score=1, score=0.3)])
    ctx.cache_hit = True
    ScoreStage("score", services).process(ctx)
    assert ctx.candidates[0].score == 0.3
