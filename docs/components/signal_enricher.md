# Signal Enricher

Annotates candidates with token counts and query overlap, and collapses duplicate passages.

| Property | Value |
|---|---|
| Stage | `signal_enricher` |
| Role | `enrich` |
| Interface | `process(ctx) -> None` |
| Critical | no |
| Source | `src/answer_or_abstain_rag/components/signal_enricher/` |
| Tests | `tests/unit/components/test_component_signal_enricher.py` |

## Behaviour

Annotates candidates with structural features and collapses exact duplicates.

## Contract

- Input is bounded by `max_input_candidates`.
- Output contains no duplicate ids.
- Never introduces candidate ids that were not in its input.
- Ordering is preserved or intentionally changed per role.

## On failure

Run degrades; candidates continue without annotations.

## Metrics

- `component_signal_enricher_runs_total`
- `component_signal_enricher_candidates_out` (histogram)
- `component_signal_enricher_removed_total`
