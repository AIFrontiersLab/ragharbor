from answer_or_abstain_rag.domain.invariants import check_outcome
from answer_or_abstain_rag.domain.models import Answer, Citation, Outcome, StageEvent


def _outcome(answer=None, reason=None, events=True):
    return Outcome(
        run_id="r", status="completed", query="q", answer=answer, abstain_reason=reason, degraded=False,
        cache_hit=False, events=[StageEvent("s")] if events else [], decisions=[], errors=[], tokens_used=0,
    )


def test_valid_outcomes_pass():
    assert check_outcome(_outcome(Answer("t", [Citation("a", 0.9), Citation("b", 0.2)]))) == []
    assert check_outcome(_outcome(reason="insufficient_evidence")) == []


def test_violations_detected():
    assert check_outcome(_outcome(Answer("t", []))) != []
    assert check_outcome(_outcome(Answer("t", [Citation("a", 0.1), Citation("b", 0.9)]))) != []
    assert check_outcome(_outcome(Answer("t", [Citation("a", 0.9), Citation("a", 0.9)]))) != []
    assert check_outcome(_outcome()) != []
    assert check_outcome(_outcome(reason="x", events=False)) != []
