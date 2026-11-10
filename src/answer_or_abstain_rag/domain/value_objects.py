"""Value objects with ordering and validation semantics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from answer_or_abstain_rag.kernel.errors import ValidationError


class Clearance(IntEnum):
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3

    @classmethod
    def parse(cls, value: str | "Clearance") -> "Clearance":
        if isinstance(value, Clearance):
            return value
        try:
            return cls[str(value).strip().upper()]
        except KeyError as exc:
            raise ValidationError(f"unknown clearance level: {value!r}") from exc

    @property
    def label(self) -> str:
        return self.name.lower()


@dataclass(frozen=True)
class Score:
    value: float

    def __post_init__(self) -> None:
        if self.value != self.value:  # NaN guard
            raise ValidationError("score must not be NaN")

    def clamp(self, low: float = 0.0, high: float = 1.0) -> "Score":
        return Score(min(high, max(low, self.value)))


@dataclass(frozen=True)
class TokenBudget:
    limit: int
    used: int = 0

    def __post_init__(self) -> None:
        if self.limit < 0 or self.used < 0:
            raise ValidationError("token budget values must be non-negative")

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.used)

    def can_afford(self, tokens: int) -> bool:
        return self.used + tokens <= self.limit

    def spend(self, tokens: int) -> "TokenBudget":
        return TokenBudget(self.limit, self.used + tokens)
