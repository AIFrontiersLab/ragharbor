"""Use-case handlers. Each handler is a single transaction around the orchestrator."""

from __future__ import annotations

from answer_or_abstain_rag.application.commands import ApproveRun, RunPipeline
from answer_or_abstain_rag.application.mappers import outcome_to_record, record_summary
from answer_or_abstain_rag.application.queries import DescribePipeline, GetRun, ListRuns
from answer_or_abstain_rag.application.unit_of_work import UnitOfWork
from answer_or_abstain_rag.domain.models import Principal, Request
from answer_or_abstain_rag.governance.rbac import Permission, authorize
from answer_or_abstain_rag.kernel.errors import NotFound


class RunPipelineHandler:
    def __init__(self, orchestrator, uow: UnitOfWork, checkpoints, clock) -> None:
        self.orchestrator = orchestrator
        self.uow = uow
        self.checkpoints = checkpoints
        self.clock = clock

    def __call__(self, command: RunPipeline) -> dict:
        request = Request.from_dict(command.request)
        authorize(request.principal, Permission.RUN_PIPELINE)
        outcome = self.orchestrator.execute(request, run_id=command.run_id)
        record = outcome_to_record(
            outcome,
            command.request,
            at=self.clock.now_iso(),
            checkpoints=self.checkpoints.load(outcome.run_id),
        )
        with self.uow:
            self.uow.add(record)
            self.uow.commit()
        return outcome.to_dict()


class ApproveRunHandler:
    def __init__(self, approvals, uow: UnitOfWork, run_handler: RunPipelineHandler) -> None:
        self.approvals = approvals
        self.uow = uow
        self.run_handler = run_handler

    def __call__(self, command: ApproveRun) -> dict:
        authorize(Principal.from_dict(command.principal, tenant="default"), Permission.APPROVE_RUN)
        record = self.uow.runs.get(command.run_id)
        if record is None:
            raise NotFound(f"run {command.run_id} not found")
        self.approvals.approve(command.run_id, command.approver)
        return self.run_handler(RunPipeline(request=record.request, run_id=command.run_id))


class GetRunHandler:
    def __init__(self, runs) -> None:
        self.runs = runs

    def __call__(self, query: GetRun) -> dict:
        record = self.runs.get(query.run_id)
        if record is None:
            raise NotFound(f"run {query.run_id} not found")
        return record.to_dict()


class ListRunsHandler:
    def __init__(self, runs) -> None:
        self.runs = runs

    def __call__(self, query: ListRuns) -> list[dict]:
        return [record_summary(r) for r in self.runs.list(limit=query.limit)]


class DescribePipelineHandler:
    def __init__(self, stages, registry) -> None:
        self.stages = stages
        self.registry = registry

    def __call__(self, query: DescribePipeline) -> dict:
        return {
            "stages": [s.describe() for s in self.stages],
            "registered": self.registry.describe(),
        }
