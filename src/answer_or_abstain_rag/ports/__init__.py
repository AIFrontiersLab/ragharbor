"""Ports: the interfaces the application core requires from the outside world.

Adapters under ``answer_or_abstain_rag.adapters`` implement these protocols. The core never
imports an adapter directly; the composition root (``container.py``) wires them.
"""

from answer_or_abstain_rag.ports.audit import AuditSink
from answer_or_abstain_rag.ports.cache import RankingCache
from answer_or_abstain_rag.ports.corpus import CorpusRepository
from answer_or_abstain_rag.ports.event_bus import EventBus
from answer_or_abstain_rag.ports.repository import RunRepository
from answer_or_abstain_rag.ports.scorer import RelevanceScorer

__all__ = ["AuditSink", "CorpusRepository", "EventBus", "RankingCache", "RelevanceScorer", "RunRepository"]
