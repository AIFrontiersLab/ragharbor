"""Ranking Cache service.

Role: ``cache``. Reuses a prior ranking for an identical tenant, principal, query, and candidate set.

Responsibility (from the architecture specification):
    Short-circuits repeated identical requests with a TTL-bounded ranking cache keyed by principal.

The service specialises :class:`CacheStage` and wraps it with this
component's contract checks, metrics, and per-run report.
"""

from __future__ import annotations

from answer_or_abstain_rag.components.ranking_cache.config import CONFIG, RankingCacheConfig
from answer_or_abstain_rag.components.ranking_cache.models import RankingCacheInput, RankingCacheReport
from answer_or_abstain_rag.components.ranking_cache.validators import validate_input, validate_output
from answer_or_abstain_rag.stages.cache import CacheStage

METRIC_PREFIX = "component_ranking_cache"
RUNS = f"{METRIC_PREFIX}_runs_total"
CANDIDATES_OUT = f"{METRIC_PREFIX}_candidates_out"
REMOVED = f"{METRIC_PREFIX}_removed_total"


def record_metrics(metrics, report: RankingCacheReport) -> None:
    if metrics is None:
        return
    metrics.inc(RUNS)
    metrics.observe(CANDIDATES_OUT, report.candidates_out)
    if report.removed:
        metrics.inc(REMOVED, len(report.removed))


class RankingCacheService(CacheStage):
    def __init__(self, services, config: RankingCacheConfig = CONFIG) -> None:
        super().__init__(config.name, services, description=config.responsibility)
        self.config = config

    def process(self, ctx) -> None:
        validate_input(ctx, self.config)
        before = RankingCacheInput.from_context(ctx)
        super().process(ctx)
        if ctx.halted and not ctx.candidates:
            report = RankingCacheReport.diff(self.name, before, [], halted=True)
        else:
            validate_output(ctx, before, self.config)
            report = RankingCacheReport.diff(self.name, before, [c.doc_id for c in ctx.candidates])
        ctx.metadata.setdefault("reports", {})[self.name] = report.to_dict()
        record_metrics(self.services.metrics, report)

    def describe(self) -> dict:
        info = super().describe()
        info.update({"display_name": self.config.display_name, "interface": self.config.interface})
        return info
