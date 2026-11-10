"""Approval Gate.

Routes runs touching restricted material to a human approver before release.
"""

from answer_or_abstain_rag.components.approval_gate.adapter import ROLE, build
from answer_or_abstain_rag.components.approval_gate.config import CONFIG, ApprovalGateConfig
from answer_or_abstain_rag.components.approval_gate.errors import ApprovalGateError
from answer_or_abstain_rag.components.approval_gate.service import ApprovalGateService

__all__ = ["CONFIG", "ROLE", "build", "ApprovalGateConfig", "ApprovalGateError", "ApprovalGateService"]
