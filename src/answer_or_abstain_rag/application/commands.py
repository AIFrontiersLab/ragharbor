"""Commands: intent to change state."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RunPipeline:
    request: dict
    run_id: str | None = None


@dataclass(frozen=True)
class ApproveRun:
    run_id: str
    approver: str
    principal: dict = field(default_factory=lambda: {"subject": "system", "roles": ["admin"]})
