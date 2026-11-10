"""Base type for domain events published on the internal event bus."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class DomainEvent:
    name: str
    run_id: str
    payload: dict = field(default_factory=dict)
    at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
