# Configuration reference

| Key | Default | Description |
|---|---|---|
| `app.environment` | `development` | Free-form environment label |
| `app.log_level` | `INFO` | Root log level |
| `pipeline.stages` | generated | Ordered stage names |
| `pipeline.top_k` | `10` | Max citations |
| `pipeline.max_candidates` | `200` | Ingest cap |
| `pipeline.require_evidence` | `true` | Abstain when no evidence survives |
| `pipeline.prior_weight` | `0.4` | Blend of upstream prior vs relevance |
| `pipeline.min_score` | `0.0` | Citation threshold |
| `pipeline.stage_timeout_ms` | `250` | Per-stage deadline (flagged, not enforced preemptively) |
| `resilience.breaker_failure_threshold` | `3` | Failures before opening |
| `resilience.breaker_reset_seconds` | `30` | Open → half-open delay |
| `resilience.retry_attempts` | `2` | Retries for retryable errors |
| `resilience.retry_base_delay` | `0.0` | Backoff base (seconds) |
| `resilience.bulkhead_limit` | `32` | Max in-flight runs |
| `resilience.rate_limit_per_second` | `50` | Per-tenant refill rate |
| `resilience.rate_limit_burst` | `100` | Per-tenant burst |
| `governance.default_clearance` | `internal` | Clearance when no role matches |
| `governance.redact_pii` | `true` | Redact PII in surviving text |
| `governance.approval_risk_threshold` | `0.8` | Risk at which approval is required |
| `governance.role_clearances` | table | Role → clearance mapping |
| `cache.enabled` | `true` | Ranking cache |
| `cache.capacity` | `1024` | Entries |
| `cache.ttl_seconds` | `300` | Entry lifetime |
| `budget.default_tokens` | `4000` | Budget when request omits one |
| `budget.hard_limit_tokens` | `32000` | Ceiling for any request |
| `http.host` / `http.port` | `127.0.0.1` / `8080` | Server bind |
| `storage.backend` | `memory` | `memory` or `jsonl` |
| `storage.path` | `var/runs` | JSONL directory |

Environment override format: `ANSWER_OR_ABSTAIN_RAG_<SECTION>__<KEY>`; lists are comma-separated.
