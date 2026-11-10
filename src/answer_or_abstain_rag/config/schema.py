"""Semantic validation for settings beyond type coercion."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.errors import ConfigurationError

CLEARANCE_LEVELS = ("public", "internal", "confidential", "restricted")


def validate_settings(settings) -> None:
    problems: list[str] = []
    p = settings.pipeline
    if p.top_k < 1:
        problems.append("pipeline.top_k must be >= 1")
    if p.max_candidates < p.top_k:
        problems.append("pipeline.max_candidates must be >= pipeline.top_k")
    if not 0.0 <= p.prior_weight <= 1.0:
        problems.append("pipeline.prior_weight must be within [0, 1]")
    if not p.stages:
        problems.append("pipeline.stages must not be empty")
    r = settings.resilience
    if r.breaker_failure_threshold < 1:
        problems.append("resilience.breaker_failure_threshold must be >= 1")
    if r.retry_attempts < 0:
        problems.append("resilience.retry_attempts must be >= 0")
    if r.bulkhead_limit < 1:
        problems.append("resilience.bulkhead_limit must be >= 1")
    g = settings.governance
    if g.default_clearance not in CLEARANCE_LEVELS:
        problems.append(f"governance.default_clearance must be one of {CLEARANCE_LEVELS}")
    for role, level in g.role_clearances.items():
        if level not in CLEARANCE_LEVELS:
            problems.append(f"governance.role_clearances.{role} has unknown level {level!r}")
    if settings.budget.default_tokens > settings.budget.hard_limit_tokens:
        problems.append("budget.default_tokens must be <= budget.hard_limit_tokens")
    if settings.storage.backend not in {"memory", "jsonl"}:
        problems.append("storage.backend must be 'memory' or 'jsonl'")
    if problems:
        raise ConfigurationError("invalid configuration", details={"problems": problems})
