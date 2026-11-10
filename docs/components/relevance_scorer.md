# Relevance Scorer

Scores query-candidate relevance with a deterministic BM25-style reference model.

| Property | Value |
|---|---|
| Stage | `relevance_scorer` |
| Role | `score` |
| Interface | `score(query, candidate) -> float` |
| Critical | no |
| Source | `src/answer_or_abstain_rag/components/relevance_scorer/` |
| Tests | `tests/unit/components/test_component_relevance_scorer.py` |

## Behaviour

Blends upstream prior scores with query-aware relevance and reorders candidates.

## Contract

- Input is bounded by `max_input_candidates`.
- Output contains no duplicate ids.
- Never introduces candidate ids that were not in its input.
- Output is sorted by descending score.

## On failure

Run degrades; fallback restores upstream prior order.

## Metrics

- `component_relevance_scorer_runs_total`
- `component_relevance_scorer_candidates_out` (histogram)
- `component_relevance_scorer_removed_total`
