"""Approval Gate service.

Role: ``approval``. Pauses high-risk result sets until a human approves the run.

Responsibility (from the architecture specification):
    Routes runs touching restricted material to a human approver before release.

The service specialises :class:`ApprovalStage` and wraps it with this
component's contract checks, metrics, and per-run report.
"""

from __future__ import annotations

from answer_or_abstain_rag.components.approval_gate.config import CONFIG, ApprovalGateConfig
from answer_or_abstain_rag.components.approval_gate.models import ApprovalGateInput, ApprovalGateReport
from answer_or_abstain_rag.components.approval_gate.validators import validate_input, validate_output
from answer_or_abstain_rag.stages.approval import ApprovalStage

METRIC_PREFIX = "component_approval_gate"
RUNS = f"{METRIC_PREFIX}_runs_total"
CANDIDATES_OUT = f"{METRIC_PREFIX}_candidates_out"
REMOVED = f"{METRIC_PREFIX}_removed_total"


def record_metrics(metrics, report: ApprovalGateReport) -> None:
    if metrics is None:
        return
    metrics.inc(RUNS)
    metrics.observe(CANDIDATES_OUT, report.candidates_out)
    if report.removed:
        metrics.inc(REMOVED, len(report.removed))


class ApprovalGateService(ApprovalStage):
    def __init__(self, services, config: ApprovalGateConfig = CONFIG) -> None:
        super().__init__(config.name, services, description=config.responsibility)
        self.config = config

    def process(self, ctx) -> None:
        validate_input(ctx, self.config)
        before = ApprovalGateInput.from_context(ctx)
        super().process(ctx)
        if ctx.halted and not ctx.candidates:
            report = ApprovalGateReport.diff(self.name, before, [], halted=True)
        else:
            validate_output(ctx, before, self.config)
            report = ApprovalGateReport.diff(self.name, before, [c.doc_id for c in ctx.candidates])
        ctx.metadata.setdefault("reports", {})[self.name] = report.to_dict()
        record_metrics(self.services.metrics, report)

    def describe(self) -> dict:
        info = super().describe()
        info.update({"display_name": self.config.display_name, "interface": self.config.interface})
        return info
