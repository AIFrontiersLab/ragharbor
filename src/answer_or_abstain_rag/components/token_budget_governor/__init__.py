"""Token Budget Governor.

Enforces per-request and global token ceilings before evidence reaches the answer stage.
"""

from answer_or_abstain_rag.components.token_budget_governor.adapter import ROLE, build
from answer_or_abstain_rag.components.token_budget_governor.config import CONFIG, TokenBudgetGovernorConfig
from answer_or_abstain_rag.components.token_budget_governor.errors import TokenBudgetGovernorError
from answer_or_abstain_rag.components.token_budget_governor.service import TokenBudgetGovernorService

__all__ = ["CONFIG", "ROLE", "build", "TokenBudgetGovernorConfig", "TokenBudgetGovernorError", "TokenBudgetGovernorService"]
