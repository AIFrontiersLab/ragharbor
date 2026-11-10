# Observability

| Signal | Source | Notes |
|---|---|---|
| Logs | `observability/logging.py` | JSON lines with `run_id`, `stage`, `request_id` |
| Traces | `observability/tracing.py` | `run` root span, `stage:<name>` children |
| Metrics | `observability/metrics.py` | Prometheus text at `/metrics` |
| Events | `adapters/outbound/event_bus.py` | Domain events with dead-letter capture |
| Checkpoints | `workflows/checkpoint.py` | Stored on every run record |

Suggested alerts: breaker open for > 5 minutes; `stage_executions_total{status="degraded"}` rate > 1%;
`pipeline_runs_total{status="failed"}` > 0; approval backlog older than SLA.
