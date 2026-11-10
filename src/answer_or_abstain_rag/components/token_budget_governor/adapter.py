"""Port and registry adapter for Token Budget Governor.

Interface from the architecture specification: ``for_request(request) -> TokenBudget``
"""

from __future__ import annotations

from typing import Protocol

from answer_or_abstain_rag.components.token_budget_governor.config import CONFIG
from answer_or_abstain_rag.components.token_budget_governor.service import TokenBudgetGovernorService
from answer_or_abstain_rag.domain.models import PipelineContext

ROLE = CONFIG.role


class TokenBudgetGovernorPort(Protocol):
    """Contract the orchestrator relies on."""

    name: str
    role: str

    def process(self, ctx: PipelineContext) -> None: ...

    def describe(self) -> dict: ...


def build(services) -> TokenBudgetGovernorService:
    return TokenBudgetGovernorService(services)
