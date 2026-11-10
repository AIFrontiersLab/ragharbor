"""Role implementations. Components specialise one of these strategies."""

from answer_or_abstain_rag.stages.answer import AnswerStage
from answer_or_abstain_rag.stages.approval import ApprovalStage
from answer_or_abstain_rag.stages.audit import AuditStage
from answer_or_abstain_rag.stages.base import Stage, StageServices
from answer_or_abstain_rag.stages.budget import BudgetStage
from answer_or_abstain_rag.stages.cache import CacheStage
from answer_or_abstain_rag.stages.enrich import EnrichStage
from answer_or_abstain_rag.stages.fallback import FallbackStage
from answer_or_abstain_rag.stages.ingest import IngestStage
from answer_or_abstain_rag.stages.policy import PolicyStage
from answer_or_abstain_rag.stages.retrieve import RetrieveStage
from answer_or_abstain_rag.stages.score import ScoreStage

ROLE_CLASSES: dict[str, type[Stage]] = {
    "ingest": IngestStage,
    "retrieve": RetrieveStage,
    "enrich": EnrichStage,
    "score": ScoreStage,
    "cache": CacheStage,
    "policy": PolicyStage,
    "budget": BudgetStage,
    "approval": ApprovalStage,
    "fallback": FallbackStage,
    "audit": AuditStage,
    "answer": AnswerStage,
}

__all__ = ["ROLE_CLASSES", "Stage", "StageServices", *[cls.__name__ for cls in ROLE_CLASSES.values()]]
