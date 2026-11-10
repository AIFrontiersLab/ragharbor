# Token Budget Governor

Enforces per-request and global token ceilings before evidence reaches the answer stage.

| Property | Value |
|---|---|
| Stage | `token_budget_governor` |
| Role | `budget` |
| Interface | `for_request(request) -> TokenBudget` |
| Critical | no |
| Source | `src/answer_or_abstain_rag/components/token_budget_governor/` |
| Tests | `tests/unit/components/test_component_token_budget_governor.py` |

## Behaviour

Keeps the highest-ranked candidates that fit inside the token budget.

## Contract

- Input is bounded by `max_input_candidates`.
- Output contains no duplicate ids.
- Never introduces candidate ids that were not in its input.
- Ordering is preserved or intentionally changed per role.

## On failure

Run degrades; the answer stage still applies `top_k`.

## Metrics

- `component_token_budget_governor_runs_total`
- `component_token_budget_governor_candidates_out` (histogram)
- `component_token_budget_governor_removed_total`
