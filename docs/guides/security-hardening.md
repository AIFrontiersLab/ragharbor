# Security hardening

- Inject a managed secret into `ApprovalService`.
- Terminate TLS at the ingress; keep the NetworkPolicy.
- Run as the non-root user defined in the Dockerfile with a read-only root filesystem.
- Ship audit JSONL to immutable storage and verify with `observability.audit.verify_chain`.
- Map identity-provider groups to `principal.groups` at the gateway; never trust client-supplied roles in production.
