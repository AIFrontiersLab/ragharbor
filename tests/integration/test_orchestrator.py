"""Orchestrator behaviour across the full, configured stage list."""

from answer_or_abstain_rag.application.commands import RunPipeline
from answer_or_abstain_rag.domain.invariants import check_outcome
from answer_or_abstain_rag.domain.models import Request


def test_every_stage_emits_an_event(container, make_request):
    result = container.bus.handle(RunPipeline(request=make_request()))
    assert [e["stage"] for e in result["events"]] == [s.name for s in container.stages]


def test_outcome_satisfies_invariants(container, make_request):
    outcome = container.orchestrator.execute(Request.from_dict(make_request()))
    assert check_outcome(outcome) == []


def test_checkpoints_and_spans_recorded(container, make_request):
    result = container.bus.handle(RunPipeline(request=make_request()))
    checkpoints = container.checkpoints.load(result["run_id"])
    assert [c["stage"] for c in checkpoints] == [s.name for s in container.stages]
    names = {s.name for s in container.tracer.spans}
    assert "run" in names and any(n.startswith("stage:") for n in names)


def test_domain_events_published(container, make_request):
    container.bus.handle(RunPipeline(request=make_request()))
    names = container.event_bus.names()
    assert names[0] == "run.started"
    assert names[-1] in {"run.completed", "run.abstained", "approval.requested"}


def test_hooks_observe_each_stage(container, make_request):
    seen = []
    container.hooks.add("after_stage", lambda stage, ctx, status: seen.append((stage.name, status)))
    container.bus.handle(RunPipeline(request=make_request()))
    assert len(seen) == len(container.stages)
