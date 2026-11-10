"""Static configuration for the Token Budget Governor component."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenBudgetGovernorConfig:
    name: str = "token_budget_governor"
    display_name: str = 'Token Budget Governor'
    role: str = "budget"
    interface: str = 'for_request(request) -> TokenBudget'
    responsibility: str = 'Enforces per-request and global token ceilings before evidence reaches the answer stage.'
    max_input_candidates: int = 10_000
    may_introduce_ids: bool = False
    enforce_sorted_output: bool = False


CONFIG = TokenBudgetGovernorConfig()
