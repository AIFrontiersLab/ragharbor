# Ranking Cache

Short-circuits repeated identical requests with a TTL-bounded ranking cache keyed by principal.

| Property | Value |
|---|---|
| Stage | `ranking_cache` |
| Role | `cache` |
| Interface | `lookup(key) -> ranking | None` |
| Critical | no |
| Source | `src/answer_or_abstain_rag/components/ranking_cache/` |
| Tests | `tests/unit/components/test_component_ranking_cache.py` |

## Behaviour

Reuses a prior ranking for an identical tenant, principal, query, and candidate set.

## Contract

- Input is bounded by `max_input_candidates`.
- Output contains no duplicate ids.
- Never introduces candidate ids that were not in its input.
- Ordering is preserved or intentionally changed per role.

## On failure

Run degrades; the request is treated as a cache miss.

## Metrics

- `component_ranking_cache_runs_total`
- `component_ranking_cache_candidates_out` (histogram)
- `component_ranking_cache_removed_total`
