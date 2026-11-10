# Token Budget Governor

Enforces per-request and global token ceilings before evidence reaches the answer stage.

| Property | Value |
|---|---|
| Stage name | `token_budget_governor` |
| Role | `budget` |
| Interface | `for_request(request) -> TokenBudget` |
| Critical | No. A failure degrades the run and downstream fallback restores a safe ordering. |
| Origin | added to complete the governed pipeline |

## Files

| File | Purpose |
|---|---|
| `config.py` | Frozen configuration dataclass and defaults |
| `service.py` | `TokenBudgetGovernorService` (role strategy plus contract checks) and metric recording |
| `validators.py` | Pre/post conditions (bounded input, no duplicate or unknown ids, ordering) |
| `models.py` | Input snapshot and per-run report |
| `errors.py` | Component error types (all `StageError` subclasses) |
| `adapter.py` | Port protocol and the factory registered in the stage registry |

## Behaviour

Keeps the highest-ranked candidates that fit inside the token budget.

See also [`docs/components/token_budget_governor.md`](../../../../docs/components/token_budget_governor.md).
