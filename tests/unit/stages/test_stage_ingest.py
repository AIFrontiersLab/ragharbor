from answer_or_abstain_rag.domain.models import PipelineContext, Request
from answer_or_abstain_rag.stages.ingest import IngestStage


def _ctx(body):
    return PipelineContext(run_id="r", request=Request.from_dict(body))


def test_dedupes_keeping_highest_prior(services):
    ctx = _ctx({"query": "q", "candidates": [{"doc_id": "a", "score": 0.1}, {"doc_id": "a", "score": 0.9}, {"doc_id": "b", "score": 0.5}]})
    IngestStage("intake", services).process(ctx)
    assert [(c.doc_id, c.prior_score) for c in ctx.candidates] == [("a", 0.9), ("b", 0.5)]


def test_synthesizes_from_evidence_ids(services):
    ctx = _ctx({"query": "q", "evidence_ids": ["e1", "e2"]})
    IngestStage("intake", services).process(ctx)
    assert [c.doc_id for c in ctx.candidates] == ["e1", "e2"]


def test_truncates_to_max_candidates(services):
    services.settings.pipeline.max_candidates = 2
    ctx = _ctx({"query": "q", "candidates": [{"doc_id": str(i), "score": i} for i in range(5)]})
    IngestStage("intake", services).process(ctx)
    assert len(ctx.candidates) == 2
    assert any(d["action"] == "truncated" for d in ctx.decisions)


def test_force_empty_evidence(services):
    ctx = _ctx({"query": "q", "evidence_ids": ["e1"], "options": {"force_empty_evidence": True}})
    IngestStage("intake", services).process(ctx)
    assert ctx.candidates == []
