# Relevance Scorer

Scores query-candidate relevance with a deterministic BM25-style reference model.

| Property | Value |
|---|---|
| Stage name | `relevance_scorer` |
| Role | `score` |
| Interface | `score(query, candidate) -> float` |
| Critical | No. A failure degrades the run and downstream fallback restores a safe ordering. |
| Origin | added to complete the governed pipeline |

## Files

| File | Purpose |
|---|---|
| `config.py` | Frozen configuration dataclass and defaults |
| `service.py` | `RelevanceScorerService` (role strategy plus contract checks) and metric recording |
| `validators.py` | Pre/post conditions (bounded input, no duplicate or unknown ids, ordering) |
| `models.py` | Input snapshot and per-run report |
| `errors.py` | Component error types (all `StageError` subclasses) |
| `adapter.py` | Port protocol and the factory registered in the stage registry |

## Behaviour

Blends upstream prior scores with query-aware relevance and reorders candidates.

See also [`docs/components/relevance_scorer.md`](../../../../docs/components/relevance_scorer.md).
