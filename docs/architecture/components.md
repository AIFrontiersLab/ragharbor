# Components (C4 level 3)

| # | Stage | Role | Critical | Source |
|---|---|---|---|---|
| 1 | `intake` (Intake) | `ingest` | yes | built-in |
| 2 | `corpus_retrieval` (Corpus Retrieval) | `retrieve` | no | built-in |
| 3 | `signal_enricher` (Signal Enricher) | `enrich` | no | [component](../components/signal_enricher.md) |
| 4 | `ranking_cache` (Ranking Cache) | `cache` | no | [component](../components/ranking_cache.md) |
| 5 | `relevance_scorer` (Relevance Scorer) | `score` | no | [component](../components/relevance_scorer.md) |
| 6 | `graceful_fallback` (Graceful Fallback) | `fallback` | no | built-in |
| 7 | `access_policy` (Access Policy) | `policy` | yes | built-in |
| 8 | `token_budget_governor` (Token Budget Governor) | `budget` | no | [component](../components/token_budget_governor.md) |
| 9 | `approval_gate` (Approval Gate) | `approval` | yes | [component](../components/approval_gate.md) |
| 10 | `audit_recorder` (Audit Recorder) | `audit` | no | [component](../components/audit_recorder.md) |
| 11 | `answer_assembly` (Answer Assembly) | `answer` | yes | built-in |

Each concept component follows the same internal layout so reviewers can navigate
any of them blind: `config.py`, `port.py`, `service.py`, `validators.py`, `models.py`,
`metrics.py`, `errors.py`, `adapter.py`.
