"""Data transfer objects that cross the application boundary."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class RunRecord:
    run_id: str
    status: str
    request: dict
    outcome: dict
    created_at: str
    updated_at: str = ""
    checkpoints: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RunRecord":
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})
