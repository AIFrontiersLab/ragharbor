"""Role-based authorization for API operations (separate from document-level access)."""

from __future__ import annotations

from enum import Enum

from answer_or_abstain_rag.domain.models import Principal
from answer_or_abstain_rag.kernel.errors import PolicyViolation


class Permission(str, Enum):
    RUN_PIPELINE = "run:create"
    READ_RUN = "run:read"
    APPROVE_RUN = "run:approve"
    READ_CONFIG = "config:read"
    READ_METRICS = "metrics:read"


ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "guest": frozenset({Permission.RUN_PIPELINE}),
    "reader": frozenset({Permission.RUN_PIPELINE, Permission.READ_RUN}),
    "analyst": frozenset({Permission.RUN_PIPELINE, Permission.READ_RUN, Permission.READ_METRICS}),
    "admin": frozenset(Permission),
}


def permissions_for(principal: Principal) -> frozenset[Permission]:
    granted: set[Permission] = set()
    for role in principal.roles:
        granted |= ROLE_PERMISSIONS.get(role, frozenset())
    return frozenset(granted)


def authorize(principal: Principal, permission: Permission) -> None:
    if permission not in permissions_for(principal):
        raise PolicyViolation(
            f"principal '{principal.subject}' lacks permission {permission.value}",
            details={"roles": list(principal.roles), "permission": permission.value},
        )
