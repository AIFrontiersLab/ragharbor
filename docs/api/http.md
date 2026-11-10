# HTTP API

All JSON responses use `{"data": ..., "request_id": "..."}`; errors use
`{"error": {"code", "message", "details"}, "request_id": "..."}`.
Send `X-Request-Id` to correlate and `X-Tenant` for rate-limit bucketing.

## POST /v1/runs

```json
{
  "query": "how is retrieval governed",
  "tenant": "acme",
  "principal": {"subject": "alice", "roles": ["reader"], "groups": ["eng"]},
  "candidates": [{"doc_id": "a", "text": "...", "score": 0.8, "classification": "internal", "acl": []}],
  "evidence_ids": [],
  "budget_tokens": 2000,
  "top_k": 5,
  "require_evidence": true,
  "options": {}
}
```

Response `data` fields: `run_id`, `status` (`completed|abstained|awaiting_approval|failed`),
`answer` (`text`, `evidence_ids`, `citations[]`), `abstain_reason`, `degraded`, `cache_hit`,
`tokens_used`, `events[]`, `decisions[]`, `errors[]`.

## Error codes

| Code | HTTP | Meaning |
|---|---|---|
| `validation_error` | 400 | Malformed request |
| `policy_violation` | 403 | Principal lacks the permission |
| `not_found` | 404 | Unknown run or path |
| `invalid_transition` | 409 | Illegal lifecycle change |
| `budget_exceeded` | 429 | Rate limit exceeded |
| `stage_error` / `circuit_open` | 503 | Capacity or dependency failure |
