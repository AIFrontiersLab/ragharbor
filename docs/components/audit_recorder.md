# Audit Recorder

Writes a hash-chainable audit record for every run, including denials and degradations.

| Property | Value |
|---|---|
| Stage | `audit_recorder` |
| Role | `audit` |
| Interface | `append(record) -> None` |
| Critical | no |
| Source | `src/answer_or_abstain_rag/components/audit_recorder/` |
| Tests | `tests/unit/components/test_component_audit_recorder.py` |

## Behaviour

Appends an immutable, redacted audit record of what the run saw and decided.

## Contract

- Input is bounded by `max_input_candidates`.
- Output contains no duplicate ids.
- Never introduces candidate ids that were not in its input.
- Ordering is preserved or intentionally changed per role.

## On failure

Run degrades; the answer is still returned and the gap is visible in metrics.

## Metrics

- `component_audit_recorder_runs_total`
- `component_audit_recorder_candidates_out` (histogram)
- `component_audit_recorder_removed_total`
