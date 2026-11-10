# Ranking Cache

Short-circuits repeated identical requests with a TTL-bounded ranking cache keyed by principal.

| Property | Value |
|---|---|
| Stage name | `ranking_cache` |
| Role | `cache` |
| Interface | `lookup(key) -> ranking | None` |
| Critical | No. A failure degrades the run and downstream fallback restores a safe ordering. |
| Origin | added to complete the governed pipeline |

## Files

| File | Purpose |
|---|---|
| `config.py` | Frozen configuration dataclass and defaults |
| `service.py` | `RankingCacheService` (role strategy plus contract checks) and metric recording |
| `validators.py` | Pre/post conditions (bounded input, no duplicate or unknown ids, ordering) |
| `models.py` | Input snapshot and per-run report |
| `errors.py` | Component error types (all `StageError` subclasses) |
| `adapter.py` | Port protocol and the factory registered in the stage registry |

## Behaviour

Reuses a prior ranking for an identical tenant, principal, query, and candidate set.

See also [`docs/components/ranking_cache.md`](../../../../docs/components/ranking_cache.md).
