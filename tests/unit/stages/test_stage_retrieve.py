from answer_or_abstain_rag.domain.models import Candidate, PipelineContext, Request
from answer_or_abstain_rag.stages.retrieve import RetrieveStage


def test_retrieves_from_corpus_when_empty(services):
    ctx = PipelineContext(run_id="r", request=Request.from_dict({"query": "hybrid retrieval recall", "tenant": "acme"}))
    RetrieveStage("retrieve", services).process(ctx)
    assert ctx.candidates and ctx.candidates[0].doc_id == "kb-001"


def test_skips_when_candidates_supplied(services):
    ctx = PipelineContext(run_id="r", request=Request.from_dict({"query": "q"}), candidates=[Candidate("x")])
    RetrieveStage("retrieve", services).process(ctx)
    assert [c.doc_id for c in ctx.candidates] == ["x"]
    assert ctx.decisions[-1]["reason"] == "candidates_supplied"
