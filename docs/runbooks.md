# Runbooks

- [Incident response](#incident-response)
- [Circuit breaker open](#circuit-breaker-open)
- [Approval backlog](#approval-backlog)
- [Cache invalidation](#cache-invalidation)
- [Scaling](#scaling)
- [Rollback](#rollback)

<a id="incident-response"></a>

## Incident response

1. Check `/readyz` for failing checks.
2. Inspect `stage_executions_total` by status to find the failing stage.
3. Pull a failing run with `GET /v1/runs/{id}` and read `errors` and `checkpoints`.
4. If a policy stage is failing, confirm runs are abstaining with `policy_unavailable` (fail-closed).
5. Roll back with the rollback runbook if the incident follows a deploy.

<a id="circuit-breaker-open"></a>

## Circuit breaker open

1. Identify the stage from `/readyz` (`breakers_closed=false`) and logs.
2. Confirm the fallback stage is restoring prior order (`restored_prior_order` decisions).
3. Fix or roll back the dependency; the breaker half-opens after `resilience.breaker_reset_seconds`.
4. A successful probe closes it; no restart needed.

<a id="approval-backlog"></a>

## Approval backlog

1. List runs with `status=awaiting_approval`.
2. Approve via `POST /v1/runs/{id}/approve` with an admin principal.
3. If the backlog is structural, review `governance.approval_risk_threshold`.

<a id="cache-invalidation"></a>

## Cache invalidation

1. Rankings are keyed by tenant, principal roles and groups, query, and candidate ids.
2. After a policy or corpus change, restart replicas or lower `cache.ttl_seconds`.
3. Disable temporarily with `ANSWER_OR_ABSTAIN_RAG_CACHE__ENABLED=false`.

<a id="scaling"></a>

## Scaling

1. Scale replicas via HPA on CPU.
2. Raise `resilience.bulkhead_limit` only with matching CPU headroom.
3. Tune per-tenant `rate_limit_per_second` for noisy neighbours.

<a id="rollback"></a>

## Rollback

1. `helm rollback <release> <revision>` or re-apply the previous image tag.
2. Verify `/readyz` and a smoke run (`scripts/smoke_test.sh`).
3. Record the incident and add a regression test.
