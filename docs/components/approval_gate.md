# Approval Gate

Routes runs touching restricted material to a human approver before release.

| Property | Value |
|---|---|
| Stage | `approval_gate` |
| Role | `approval` |
| Interface | `approve(run_id, approver) -> token` |
| Critical | yes |
| Source | `src/answer_or_abstain_rag/components/approval_gate/` |
| Tests | `tests/unit/components/test_component_approval_gate.py` |

## Behaviour

Pauses high-risk result sets until a human approves the run.

## Contract

- Input is bounded by `max_input_candidates`.
- Output contains no duplicate ids.
- Never introduces candidate ids that were not in its input.
- Ordering is preserved or intentionally changed per role.

## On failure

Run fails; nothing is released without an approval decision.

## Metrics

- `component_approval_gate_runs_total`
- `component_approval_gate_candidates_out` (histogram)
- `component_approval_gate_removed_total`
