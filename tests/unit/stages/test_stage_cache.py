from answer_or_abstain_rag.domain.models import Candidate, PipelineContext, Request
from answer_or_abstain_rag.stages.cache import CacheStage, cache_key


def _ctx(roles=("reader",)):
    return PipelineContext(
        run_id="r",
        request=Request.from_dict({"query": "Q", "principal": {"roles": list(roles)}}),
        candidates=[Candidate("a", score=0.1), Candidate("b", score=0.2)],
    )


def test_miss_then_hit(services):
    stage = CacheStage("cache", services)
    first = _ctx()
    stage.process(first)
    assert not first.cache_hit
    services.cache.put(first.metadata["cache_key"], [("b", 0.9), ("a", 0.4)])
    second = _ctx()
    stage.process(second)
    assert second.cache_hit
    assert [(c.doc_id, c.score) for c in second.candidates] == [("b", 0.9), ("a", 0.4)]


def test_key_depends_on_principal():
    assert cache_key(_ctx(("reader",))) != cache_key(_ctx(("admin",)))
