"""Concept-specific components. Each one specialises a stage role with its own
configuration, validation, metrics, and errors."""

from answer_or_abstain_rag.components.approval_gate import adapter as _approval_gate
from answer_or_abstain_rag.components.audit_recorder import adapter as _audit_recorder
from answer_or_abstain_rag.components.ranking_cache import adapter as _ranking_cache
from answer_or_abstain_rag.components.relevance_scorer import adapter as _relevance_scorer
from answer_or_abstain_rag.components.signal_enricher import adapter as _signal_enricher
from answer_or_abstain_rag.components.token_budget_governor import adapter as _token_budget_governor

COMPONENT_FACTORIES = {
    "signal_enricher": (_signal_enricher.ROLE, _signal_enricher.build),
    "ranking_cache": (_ranking_cache.ROLE, _ranking_cache.build),
    "token_budget_governor": (_token_budget_governor.ROLE, _token_budget_governor.build),
    "audit_recorder": (_audit_recorder.ROLE, _audit_recorder.build),
    "approval_gate": (_approval_gate.ROLE, _approval_gate.build),
    "relevance_scorer": (_relevance_scorer.ROLE, _relevance_scorer.build),
}
