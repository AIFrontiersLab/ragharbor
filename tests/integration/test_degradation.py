"""Failure injection: non-critical stages degrade, critical stages stop the run, policy fails closed."""

import pytest

from answer_or_abstain_rag.application.commands import RunPipeline
from answer_or_abstain_rag.resilience.circuit_breaker import BreakerState


def _non_critical(container):
    return [s for s in container.stages if not s.critical]


def _critical_policy(container):
    return next(s for s in container.stages if s.role == "policy")


def test_non_critical_failure_degrades_but_answers(container, make_request):
    stages = _non_critical(container)
    if not stages:
        pytest.skip("pipeline has no non-critical stages")
    target = stages[0].name
    result = container.bus.handle(RunPipeline(request=make_request(options={"fail_stages": [target]})))
    assert result["degraded"] is True
    assert result["status"] in {"completed", "abstained", "awaiting_approval"}
    assert any(e["stage"] == target and e["status"] == "degraded" for e in result["events"])


def test_policy_failure_fails_closed(container, make_request):
    policy = _critical_policy(container)
    result = container.bus.handle(RunPipeline(request=make_request(options={"fail_stages": [policy.name]})))
    assert result["answer"] is None
    assert result["abstain_reason"] == "policy_unavailable"


def test_breaker_opens_after_repeated_failures(container, make_request):
    stages = _non_critical(container)
    if not stages:
        pytest.skip("pipeline has no non-critical stages")
    target = stages[0].name
    threshold = container.settings.resilience.breaker_failure_threshold
    for _ in range(threshold):
        container.bus.handle(RunPipeline(request=make_request(options={"fail_stages": [target]})))
    assert container.breakers[target].state is BreakerState.OPEN
    result = container.bus.handle(RunPipeline(request=make_request()))
    assert any(e["stage"] == target and e["detail"].get("error") == "circuit_open" for e in result["events"])
    assert container.health.run()["checks"]["breakers_closed"] is False
