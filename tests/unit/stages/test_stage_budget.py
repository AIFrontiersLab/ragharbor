from answer_or_abstain_rag.domain.models import Candidate, PipelineContext, Request
from answer_or_abstain_rag.stages.budget import BudgetStage


def _ctx(budget):
    return PipelineContext(
        run_id="r",
        request=Request.from_dict({"query": "q", "budget_tokens": budget}),
        candidates=[Candidate("a", "x" * 40), Candidate("b", "y" * 40), Candidate("c", "z" * 40)],
    )


def test_keeps_prefix_within_budget(services):
    ctx = _ctx(25)
    BudgetStage("budget", services).process(ctx)
    assert [c.doc_id for c in ctx.candidates] == ["a", "b"]
    assert ctx.tokens_used == 22


def test_zero_budget_abstains(services):
    ctx = _ctx(0)
    BudgetStage("budget", services).process(ctx)
    assert ctx.abstain_reason == "budget_exhausted"
