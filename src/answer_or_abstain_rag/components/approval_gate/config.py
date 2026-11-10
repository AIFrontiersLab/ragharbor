"""Static configuration for the Approval Gate component."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApprovalGateConfig:
    name: str = "approval_gate"
    display_name: str = 'Approval Gate'
    role: str = "approval"
    interface: str = 'approve(run_id, approver) -> token'
    responsibility: str = 'Routes runs touching restricted material to a human approver before release.'
    max_input_candidates: int = 10_000
    may_introduce_ids: bool = False
    enforce_sorted_output: bool = False


CONFIG = ApprovalGateConfig()
