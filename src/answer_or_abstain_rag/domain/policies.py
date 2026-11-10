"""Pure access rules. Governance services compose these; they never do I/O."""

from __future__ import annotations

from answer_or_abstain_rag.domain.models import Candidate, Principal
from answer_or_abstain_rag.domain.value_objects import Clearance


def principal_clearance(principal: Principal, role_clearances: dict, default: str) -> Clearance:
    levels = [Clearance.parse(role_clearances[r]) for r in principal.roles if r in role_clearances]
    return max(levels) if levels else Clearance.parse(default)


def clearance_allows(clearance: Clearance, candidate: Candidate) -> bool:
    return clearance >= Clearance.parse(candidate.classification)


def acl_allows(principal: Principal, candidate: Candidate) -> bool:
    """Empty ACL means "anyone with sufficient clearance". Otherwise require a shared group."""
    if not candidate.acl:
        return True
    return bool(set(candidate.acl) & (set(principal.groups) | {principal.subject}))


def tenant_allows(principal: Principal, candidate: Candidate) -> bool:
    owner = candidate.metadata.get("tenant")
    return owner is None or owner == principal.tenant
