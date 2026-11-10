"""Port and registry adapter for Approval Gate.

Interface from the architecture specification: ``approve(run_id, approver) -> token``
"""

from __future__ import annotations

from typing import Protocol

from answer_or_abstain_rag.components.approval_gate.config import CONFIG
from answer_or_abstain_rag.components.approval_gate.service import ApprovalGateService
from answer_or_abstain_rag.domain.models import PipelineContext

ROLE = CONFIG.role


class ApprovalGatePort(Protocol):
    """Contract the orchestrator relies on."""

    name: str
    role: str

    def process(self, ctx: PipelineContext) -> None: ...

    def describe(self) -> dict: ...


def build(services) -> ApprovalGateService:
    return ApprovalGateService(services)
