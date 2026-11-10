"""Human-in-the-loop approval: a high-risk run pauses, an admin approves, the run completes."""

import pytest

from answer_or_abstain_rag.application.commands import ApproveRun, RunPipeline
from answer_or_abstain_rag.kernel.errors import PolicyViolation


@pytest.fixture
def approval_container(settings, clock, corpus):
    from answer_or_abstain_rag.container import build_container
    from answer_or_abstain_rag.stage_catalog import BUILTINS, COMPONENTS

    roles = {**BUILTINS, **{c["slug"]: c["role"] for c in COMPONENTS}}
    if "approval" not in {roles[s] for s in settings.pipeline.stages}:
        approval_stage = next((n for n, r in roles.items() if r == "approval"), None)
        if approval_stage is None:
            pytest.skip("no approval stage registered")
        settings.pipeline.stages.insert(len(settings.pipeline.stages) - 1, approval_stage)
    return build_container(settings, clock=clock, corpus=corpus)


def _restricted_request():
    return {
        "query": "incident report retrieval breach",
        "principal": {"subject": "root", "roles": ["admin"]},
        "candidates": [{"doc_id": "ir-1", "text": "Restricted incident report on retrieval breach", "score": 0.9, "classification": "restricted"}],
    }


def test_restricted_run_awaits_then_completes(approval_container):
    bus = approval_container.bus
    first = bus.handle(RunPipeline(request=_restricted_request()))
    assert first["status"] == "awaiting_approval"
    assert first["abstain_reason"] == "approval_required"
    second = bus.handle(ApproveRun(run_id=first["run_id"], approver="ciso"))
    assert second["status"] == "completed"
    assert second["answer"]["evidence_ids"] == ["ir-1"]


def test_only_admins_can_approve(approval_container):
    first = approval_container.bus.handle(RunPipeline(request=_restricted_request()))
    with pytest.raises(PolicyViolation):
        approval_container.bus.handle(ApproveRun(run_id=first["run_id"], approver="x", principal={"roles": ["reader"]}))
