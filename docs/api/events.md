# Domain events

| Event | When | Payload |
|---|---|---|
| `run.started` | bulkhead slot acquired | `tenant` |
| `stage.degraded` | non-critical stage failed | `stage` |
| `candidate.denied` | policy removed candidates | `count` |
| `approval.requested` | run paused for approval | |
| `run.completed` | answer released | `citations` |
| `run.abstained` | no answer | `reason` |
| `run.failed` | critical stage failed | `reason` |

Subscribe with `container.event_bus.subscribe(name, handler)`; use `"*"` for all events.
Handler exceptions are captured in `dead_letters`, never propagated.
