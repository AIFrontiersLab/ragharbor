"""End-to-end behaviour through the message bus."""

from answer_or_abstain_rag.application.commands import RunPipeline


def test_governed_answer_excludes_unauthorised_material(container, make_request):
    result = container.bus.handle(RunPipeline(request=make_request()))
    assert result["status"] == "completed"
    cited = result["answer"]["evidence_ids"]
    assert "doc-d" not in cited, "restricted document must never be cited for a reader"
    assert cited, "authorised evidence should be cited"


def test_relevant_document_outranks_high_prior_noise(container, make_request):
    result = container.bus.handle(RunPipeline(request=make_request()))
    cited = result["answer"]["evidence_ids"]
    assert cited.index("doc-a") < cited.index("doc-b")


def test_corpus_retrieval_when_no_candidates(container):
    result = container.bus.handle(RunPipeline(request={"query": "reranking retrieved candidates relevance", "tenant": "acme"}))
    assert "kb-002" in result["answer"]["evidence_ids"]


def test_abstains_when_nothing_relevant(container):
    result = container.bus.handle(RunPipeline(request={"query": "zebra migration antarctica", "tenant": "acme"}))
    assert result["abstain"] and result["abstain_reason"] == "insufficient_evidence"


def test_run_is_persisted_and_listed(container, make_request):
    from answer_or_abstain_rag.application.queries import GetRun, ListRuns

    result = container.bus.handle(RunPipeline(request=make_request()))
    stored = container.bus.handle(GetRun(run_id=result["run_id"]))
    assert stored["outcome"]["run_id"] == result["run_id"]
    assert container.bus.handle(ListRuns())[0]["run_id"] == result["run_id"]


def test_policy_violation_for_unknown_role(container, make_request):
    import pytest

    from answer_or_abstain_rag.kernel.errors import PolicyViolation

    with pytest.raises(PolicyViolation):
        container.bus.handle(RunPipeline(request=make_request(principal={"roles": ["nobody"]})))
