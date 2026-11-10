# Signal Enricher

Annotates candidates with token counts and query overlap, and collapses duplicate passages.

| Property | Value |
|---|---|
| Stage name | `signal_enricher` |
| Role | `enrich` |
| Interface | `process(ctx) -> None` |
| Critical | No. A failure degrades the run and downstream fallback restores a safe ordering. |
| Origin | added to complete the governed pipeline |

## Files

| File | Purpose |
|---|---|
| `config.py` | Frozen configuration dataclass and defaults |
| `service.py` | `SignalEnricherService` (role strategy plus contract checks) and metric recording |
| `validators.py` | Pre/post conditions (bounded input, no duplicate or unknown ids, ordering) |
| `models.py` | Input snapshot and per-run report |
| `errors.py` | Component error types (all `StageError` subclasses) |
| `adapter.py` | Port protocol and the factory registered in the stage registry |

## Behaviour

Annotates candidates with structural features and collapses exact duplicates.

See also [`docs/components/signal_enricher.md`](../../../../docs/components/signal_enricher.md).
