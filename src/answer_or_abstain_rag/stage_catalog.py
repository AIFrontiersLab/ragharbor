"""Stage catalog for Answer-or-Abstain RAG.

Declares the default stage order and registers every built-in and component stage
with the plugin registry. Imports of stage classes are deferred so configuration
modules can read ``DEFAULT_STAGE_ORDER`` without import cycles.
"""

from __future__ import annotations

DEFAULT_STAGE_ORDER = [
    "intake",
    "corpus_retrieval",
    "signal_enricher",
    "ranking_cache",
    "relevance_scorer",
    "graceful_fallback",
    "access_policy",
    "token_budget_governor",
    "approval_gate",
    "audit_recorder",
    "answer_assembly",
]

BUILTINS = {
    "intake": "ingest",
    "corpus_retrieval": "retrieve",
    "relevance_scoring": "score",
    "access_policy": "policy",
    "graceful_fallback": "fallback",
    "answer_assembly": "answer",
}

COMPONENTS = [
    {"name": 'Signal Enricher', "slug": "signal_enricher", "role": "enrich", "origin": "padded"},
    {"name": 'Ranking Cache', "slug": "ranking_cache", "role": "cache", "origin": "padded"},
    {"name": 'Token Budget Governor', "slug": "token_budget_governor", "role": "budget", "origin": "padded"},
    {"name": 'Audit Recorder', "slug": "audit_recorder", "role": "audit", "origin": "padded"},
    {"name": 'Approval Gate', "slug": "approval_gate", "role": "approval", "origin": "padded"},
    {"name": 'Relevance Scorer', "slug": "relevance_scorer", "role": "score", "origin": "padded"},
]


def register_all(registry) -> None:
    from answer_or_abstain_rag.components import COMPONENT_FACTORIES
    from answer_or_abstain_rag.stages import ROLE_CLASSES

    for name, role in BUILTINS.items():
        cls = ROLE_CLASSES[role]
        registry.register(name, role, lambda services, cls=cls, name=name: cls(name, services), source="builtin")
    for name, (role, factory) in COMPONENT_FACTORIES.items():
        registry.register(name, role, factory, source="component")
