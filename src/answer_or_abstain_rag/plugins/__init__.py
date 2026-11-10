"""Extension points: stage factories and lifecycle hooks."""

from answer_or_abstain_rag.plugins.hooks import HookManager
from answer_or_abstain_rag.plugins.registry import StageRegistry

__all__ = ["HookManager", "StageRegistry"]
