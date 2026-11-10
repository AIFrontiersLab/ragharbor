"""Relevance Scorer service.

Role: ``score``. Blends upstream prior scores with query-aware relevance and reorders candidates.

Responsibility (from the architecture specification):
    Scores query-candidate relevance with a deterministic BM25-style reference model.

The service specialises :class:`ScoreStage` and wraps it with this
component's contract checks, metrics, and per-run report.
"""

from __future__ import annotations

from answer_or_abstain_rag.components.relevance_scorer.config import CONFIG, RelevanceScorerConfig
from answer_or_abstain_rag.components.relevance_scorer.models import RelevanceScorerInput, RelevanceScorerReport
from answer_or_abstain_rag.components.relevance_scorer.validators import validate_input, validate_output
from answer_or_abstain_rag.stages.score import ScoreStage

METRIC_PREFIX = "component_relevance_scorer"
RUNS = f"{METRIC_PREFIX}_runs_total"
CANDIDATES_OUT = f"{METRIC_PREFIX}_candidates_out"
REMOVED = f"{METRIC_PREFIX}_removed_total"


def record_metrics(metrics, report: RelevanceScorerReport) -> None:
    if metrics is None:
        return
    metrics.inc(RUNS)
    metrics.observe(CANDIDATES_OUT, report.candidates_out)
    if report.removed:
        metrics.inc(REMOVED, len(report.removed))


class RelevanceScorerService(ScoreStage):
    def __init__(self, services, config: RelevanceScorerConfig = CONFIG) -> None:
        super().__init__(config.name, services, description=config.responsibility)
        self.config = config

    def process(self, ctx) -> None:
        validate_input(ctx, self.config)
        before = RelevanceScorerInput.from_context(ctx)
        super().process(ctx)
        if ctx.halted and not ctx.candidates:
            report = RelevanceScorerReport.diff(self.name, before, [], halted=True)
        else:
            validate_output(ctx, before, self.config)
            report = RelevanceScorerReport.diff(self.name, before, [c.doc_id for c in ctx.candidates])
        ctx.metadata.setdefault("reports", {})[self.name] = report.to_dict()
        record_metrics(self.services.metrics, report)

    def describe(self) -> dict:
        info = super().describe()
        info.update({"display_name": self.config.display_name, "interface": self.config.interface})
        return info
