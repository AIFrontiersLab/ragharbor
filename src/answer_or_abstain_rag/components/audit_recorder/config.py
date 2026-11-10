"""Static configuration for the Audit Recorder component."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuditRecorderConfig:
    name: str = "audit_recorder"
    display_name: str = 'Audit Recorder'
    role: str = "audit"
    interface: str = 'append(record) -> None'
    responsibility: str = 'Writes a hash-chainable audit record for every run, including denials and degradations.'
    max_input_candidates: int = 10_000
    may_introduce_ids: bool = False
    enforce_sorted_output: bool = False


CONFIG = AuditRecorderConfig()
