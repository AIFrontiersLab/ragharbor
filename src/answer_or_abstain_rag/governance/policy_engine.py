"""Document-level access decisions composed from pure domain rules.

Rules are evaluated in order; the first denial wins (deny-overrides). Every
decision carries a reason so denials are explainable in the audit trail.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from answer_or_abstain_rag.domain import policies
from answer_or_abstain_rag.domain.models import Candidate, Principal


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str = "allowed"


Rule = Callable[[Principal, Candidate], Decision | None]


class PolicyEngine:
    def __init__(self, role_clearances: dict, default_clearance: str, *, extra_rules: list[Rule] | None = None) -> None:
        self.role_clearances = dict(role_clearances)
        self.default_clearance = default_clearance
        self.rules: list[Rule] = [self._tenant_rule, self._clearance_rule, self._acl_rule, *(extra_rules or [])]

    def evaluate(self, principal: Principal, candidate: Candidate) -> Decision:
        for rule in self.rules:
            verdict = rule(principal, candidate)
            if verdict is not None and not verdict.allowed:
                return verdict
        return Decision(True)

    def _tenant_rule(self, principal: Principal, candidate: Candidate) -> Decision | None:
        return None if policies.tenant_allows(principal, candidate) else Decision(False, "tenant_mismatch")

    def _clearance_rule(self, principal: Principal, candidate: Candidate) -> Decision | None:
        level = policies.principal_clearance(principal, self.role_clearances, self.default_clearance)
        return None if policies.clearance_allows(level, candidate) else Decision(False, "insufficient_clearance")

    def _acl_rule(self, principal: Principal, candidate: Candidate) -> Decision | None:
        return None if policies.acl_allows(principal, candidate) else Decision(False, "acl_denied")
