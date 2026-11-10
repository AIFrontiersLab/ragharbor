# Security

| Threat | Control |
|---|---|
| Cross-tenant data exposure | Tenant rule evaluated first in the policy engine; corpus search is tenant-scoped |
| Privilege escalation via documents | Clearance ordering + group ACLs; deny overrides |
| Sensitive data in answers | PII redaction before answer assembly |
| Unauthorised approvals | `run:approve` permission required; HMAC approval tokens |
| Policy dependency outage | Policy stage is critical and fails closed |
| Request floods | Per-tenant token bucket, process bulkhead, body size limit |
| Log leakage | Audit records store query length, not query text |

Hardening checklist: [guides/security-hardening.md](../guides/security-hardening.md).
