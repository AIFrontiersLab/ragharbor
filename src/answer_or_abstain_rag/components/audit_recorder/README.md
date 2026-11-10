# Audit Recorder

Writes a hash-chainable audit record for every run, including denials and degradations.

| Property | Value |
|---|---|
| Stage name | `audit_recorder` |
| Role | `audit` |
| Interface | `append(record) -> None` |
| Critical | No. A failure degrades the run and downstream fallback restores a safe ordering. |
| Origin | added to complete the governed pipeline |

## Files

| File | Purpose |
|---|---|
| `config.py` | Frozen configuration dataclass and defaults |
| `service.py` | `AuditRecorderService` (role strategy plus contract checks) and metric recording |
| `validators.py` | Pre/post conditions (bounded input, no duplicate or unknown ids, ordering) |
| `models.py` | Input snapshot and per-run report |
| `errors.py` | Component error types (all `StageError` subclasses) |
| `adapter.py` | Port protocol and the factory registered in the stage registry |

## Behaviour

Appends an immutable, redacted audit record of what the run saw and decided.

See also [`docs/components/audit_recorder.md`](../../../../docs/components/audit_recorder.md).
