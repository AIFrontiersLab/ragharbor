import pytest

from answer_or_abstain_rag.adapters.outbound.audit_sink import InMemoryAuditSink, JsonlAuditSink
from answer_or_abstain_rag.adapters.outbound.event_bus import InMemoryEventBus
from answer_or_abstain_rag.adapters.outbound.jsonl_repository import JsonlRunRepository
from answer_or_abstain_rag.adapters.outbound.lexical_scorer import LexicalScorer
from answer_or_abstain_rag.adapters.outbound.memory_corpus import InMemoryCorpus
from answer_or_abstain_rag.adapters.outbound.memory_repository import InMemoryRunRepository
from answer_or_abstain_rag.adapters.outbound.ttl_cache import TTLRankingCache
from answer_or_abstain_rag.application.dto import RunRecord
from answer_or_abstain_rag.domain.models import Candidate
from answer_or_abstain_rag.kernel.clock import FakeClock
from answer_or_abstain_rag.kernel.events import DomainEvent

# --- test_audit_sink.py ----------------------------------------------------

def test_sinks_round_trip(tmp_path):
    for sink in (InMemoryAuditSink(), JsonlAuditSink(tmp_path / "audit.jsonl")):
        sink.append({"run_id": "r1"})
        sink.append({"run_id": "r2"})
        assert [r["run_id"] for r in sink.records()] == ["r1", "r2"]


# --- test_event_bus.py -----------------------------------------------------

def test_specific_and_wildcard_subscribers_and_dead_letters():
    bus = InMemoryEventBus()
    seen = []
    bus.subscribe("run.started", lambda e: seen.append(("specific", e.name)))
    bus.subscribe("*", lambda e: seen.append(("any", e.name)))
    bus.subscribe("run.started", lambda e: 1 / 0)
    bus.publish(DomainEvent("run.started", "r"))
    assert ("specific", "run.started") in seen and ("any", "run.started") in seen
    assert len(bus.dead_letters) == 1
    assert bus.names() == ["run.started"]


# --- test_lexical_scorer.py ------------------------------------------------

def test_scores_are_bounded_and_ordered():
    scorer = LexicalScorer()
    strong = scorer.score("policy retrieval", Candidate("a", "policy retrieval policy retrieval"))
    weak = scorer.score("policy retrieval", Candidate("b", "policy only here"))
    none = scorer.score("policy retrieval", Candidate("c", "unrelated"))
    assert 0.0 <= none < weak < strong <= 1.0


def test_empty_inputs_score_zero():
    assert LexicalScorer().score("", Candidate("a", "x")) == 0.0


# --- test_memory_corpus.py -------------------------------------------------

def test_search_ranks_by_overlap_and_respects_tenant(corpus):
    hits = corpus.search("globex onboarding retrieval", tenant="acme", limit=5)
    assert "kb-007" not in [h.doc_id for h in hits]
    own = corpus.search("globex onboarding", tenant="globex", limit=5)
    assert own[0].doc_id == "kb-007"


def test_from_json(tmp_path):
    path = tmp_path / "c.json"
    path.write_text('[{"doc_id": "x", "text": "alpha beta"}]')
    corpus = InMemoryCorpus.from_json(path)
    assert len(corpus) == 1
    assert corpus.search("beta", tenant="t", limit=1)[0].prior_score == 1.0


# --- test_repositories.py --------------------------------------------------

def _rec(run_id, status="completed"):
    return RunRecord(run_id=run_id, status=status, request={"query": "q"}, outcome={}, created_at="t")


@pytest.fixture(params=["memory", "jsonl"])
def repo(request, tmp_path):
    return InMemoryRunRepository() if request.param == "memory" else JsonlRunRepository(tmp_path)


def test_add_get_list_remove(repo):
    repo.add(_rec("a"))
    repo.add(_rec("b"))
    repo.add(_rec("a", status="abstained"))
    assert repo.get("a").status == "abstained"
    assert [r.run_id for r in repo.list()] == ["a", "b"]
    repo.remove("a")
    assert repo.get("a") is None


def test_memory_capacity_evicts_oldest():
    repo = InMemoryRunRepository(capacity=2)
    for rid in "xyz":
        repo.add(_rec(rid))
    assert repo.get("x") is None and len(repo) == 2


# --- test_ttl_cache.py -----------------------------------------------------

def test_ttl_expiry_and_lru_eviction():
    clock = FakeClock()
    cache = TTLRankingCache(capacity=2, ttl_seconds=10, clock=clock)
    cache.put("a", [("x", 1.0)])
    cache.put("b", [("y", 1.0)])
    cache.get("a")
    cache.put("c", [("z", 1.0)])
    assert cache.get("b") is None and cache.get("a") is not None
    clock.advance(11)
    assert cache.get("a") is None
    assert cache.hits == 2 and cache.misses == 2


def test_invalidate():
    cache = TTLRankingCache()
    cache.put("a", [])
    cache.invalidate("a")
    assert cache.get("a") is None
    cache.put("b", [])
    cache.invalidate()
    assert len(cache) == 0
