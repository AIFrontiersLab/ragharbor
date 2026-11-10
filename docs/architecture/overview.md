# Architecture overview

Detect insufficient evidence before generating an answer.

## Goals

1. Correctness first: an answer is released only with evidence the caller is entitled to see.
2. Explainability: every inclusion, exclusion, and degradation is recorded as a decision.
3. Graceful degradation: optional stages may fail without taking the service down.
4. Replaceability: every external dependency sits behind a port.

## Style

**Hexagonal pipeline with pluggable stages**, realised as hexagonal architecture with a strategy-based stage pipeline.

```mermaid
flowchart TB
    subgraph Inbound[Inbound adapters]
        http[WSGI HTTP API]
        cli[CLI]
    end
    subgraph Application
        bus[Message bus] --> handlers[Use-case handlers]
        handlers --> orch[Orchestrator]
        handlers --> uow[Unit of work]
    end
    subgraph Core[Domain + stages]
        stages[Stage strategies] --> domain[Domain model and rules]
        components[Concept components] --> stages
    end
    subgraph CrossCutting[Cross-cutting]
        res[Resilience]
        gov[Governance]
        obs[Observability]
        wf[Workflows]
    end
    subgraph Outbound[Outbound adapters]
        repo[Run repositories]
        corpus[Corpus]
        cache[TTL cache]
        events[Event bus]
        audit[Audit sinks]
    end
    http --> bus
    cli --> bus
    orch --> stages
    orch --> res
    orch --> obs
    orch --> wf
    stages --> gov
    stages -. ports .-> Outbound
    uow -. ports .-> repo
```

## Stage pipeline

1. `intake` (ingest): Validates, normalises, de-duplicates, and bounds the incoming candidate set.
2. `corpus_retrieval` (retrieve): Pulls candidates from the corpus when the caller did not supply any.
3. `signal_enricher` (enrich): Annotates candidates with structural features and collapses exact duplicates.
4. `ranking_cache` (cache): Reuses a prior ranking for an identical tenant, principal, query, and candidate set.
5. `relevance_scorer` (score): Blends upstream prior scores with query-aware relevance and reorders candidates.
6. `graceful_fallback` (fallback): Restores a safe prior-score ordering when an upstream stage degraded.
7. `access_policy` (policy): Fail-closed tenant, clearance, and ACL filtering plus PII redaction.
8. `token_budget_governor` (budget): Keeps the highest-ranked candidates that fit inside the token budget.
9. `approval_gate` (approval): Pauses high-risk result sets until a human approves the run.
10. `audit_recorder` (audit): Appends an immutable, redacted audit record of what the run saw and decided.
11. `answer_assembly` (answer): Assembles a citation-backed answer, or abstains when evidence is insufficient.

## Key modules

| Module | Responsibility |
|---|---|
| `application/orchestrator.py` | Executes stages with breakers, retries, deadlines, spans, checkpoints |
| `stage_catalog.py` | Default topology and registry wiring |
| `container.py` | Composition root |
| `governance/policy_engine.py` | Deny-overrides access decisions |
| `workflows/state_machine.py` | Legal run lifecycle transitions |
