# Governance

Two layers of authorization are deliberately separate:

1. **Operation-level (RBAC)** in `governance/rbac.py`: may this principal create, read, or approve runs?
2. **Data-level (ABAC)** in `governance/policy_engine.py`: may this principal see this document?

Policy rules are pure functions in `domain/policies.py`, which keeps them trivially testable.
Custom rules are appended with `PolicyEngine(extra_rules=[...])`; any rule may deny, none may override a denial.

Approvals: runs whose highest classification yields risk ≥ `governance.approval_risk_threshold`
transition to `awaiting_approval`. `POST /v1/runs/{id}/approve` re-executes the stored request under
the same run id once approved.
