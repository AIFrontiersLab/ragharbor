# Approval Gate

Routes runs touching restricted material to a human approver before release.

| Property | Value |
|---|---|
| Stage name | `approval_gate` |
| Role | `approval` |
| Interface | `approve(run_id, approver) -> token` |
| Critical | Yes. A failure stops the run. |
| Origin | added to complete the governed pipeline |

## Files

| File | Purpose |
|---|---|
| `config.py` | Frozen configuration dataclass and defaults |
| `service.py` | `ApprovalGateService` (role strategy plus contract checks) and metric recording |
| `validators.py` | Pre/post conditions (bounded input, no duplicate or unknown ids, ordering) |
| `models.py` | Input snapshot and per-run report |
| `errors.py` | Component error types (all `StageError` subclasses) |
| `adapter.py` | Port protocol and the factory registered in the stage registry |

## Behaviour

Pauses high-risk result sets until a human approves the run.

See also [`docs/components/approval_gate.md`](../../../../docs/components/approval_gate.md).
