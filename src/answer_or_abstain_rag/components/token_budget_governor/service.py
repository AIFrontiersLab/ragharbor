"""Token Budget Governor service.

Role: ``budget``. Keeps the highest-ranked candidates that fit inside the token budget.

Responsibility (from the architecture specification):
    Enforces per-request and global token ceilings before evidence reaches the answer stage.

The service specialises :class:`BudgetStage` and wraps it with this
component's contract checks, metrics, and per-run report.
"""

from __future__ import annotations

from answer_or_abstain_rag.components.token_budget_governor.config import CONFIG, TokenBudgetGovernorConfig
from answer_or_abstain_rag.components.token_budget_governor.models import TokenBudgetGovernorInput, TokenBudgetGovernorReport
from answer_or_abstain_rag.components.token_budget_governor.validators import validate_input, validate_output
from answer_or_abstain_rag.stages.budget import BudgetStage

METRIC_PREFIX = "component_token_budget_governor"
RUNS = f"{METRIC_PREFIX}_runs_total"
CANDIDATES_OUT = f"{METRIC_PREFIX}_candidates_out"
REMOVED = f"{METRIC_PREFIX}_removed_total"


def record_metrics(metrics, report: TokenBudgetGovernorReport) -> None:
    if metrics is None:
        return
    metrics.inc(RUNS)
    metrics.observe(CANDIDATES_OUT, report.candidates_out)
    if report.removed:
        metrics.inc(REMOVED, len(report.removed))


class TokenBudgetGovernorService(BudgetStage):
    def __init__(self, services, config: TokenBudgetGovernorConfig = CONFIG) -> None:
        super().__init__(config.name, services, description=config.responsibility)
        self.config = config

    def process(self, ctx) -> None:
        validate_input(ctx, self.config)
        before = TokenBudgetGovernorInput.from_context(ctx)
        super().process(ctx)
        if ctx.halted and not ctx.candidates:
            report = TokenBudgetGovernorReport.diff(self.name, before, [], halted=True)
        else:
            validate_output(ctx, before, self.config)
            report = TokenBudgetGovernorReport.diff(self.name, before, [c.doc_id for c in ctx.candidates])
        ctx.metadata.setdefault("reports", {})[self.name] = report.to_dict()
        record_metrics(self.services.metrics, report)

    def describe(self) -> dict:
        info = super().describe()
        info.update({"display_name": self.config.display_name, "interface": self.config.interface})
        return info
