"""Saga: run steps in order; on failure, compensate completed steps in reverse order."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class SagaStep:
    name: str
    action: Callable[[dict], None]
    compensate: Callable[[dict], None] | None = None


class SagaFailed(RuntimeError):
    def __init__(self, step: str, cause: Exception, compensated: list[str]) -> None:
        super().__init__(f"saga failed at step '{step}': {cause}")
        self.step = step
        self.cause = cause
        self.compensated = compensated


class Saga:
    def __init__(self, steps: list[SagaStep]) -> None:
        self.steps = steps

    def execute(self, state: dict) -> dict:
        done: list[SagaStep] = []
        for step in self.steps:
            try:
                step.action(state)
            except Exception as exc:
                compensated = []
                for prior in reversed(done):
                    if prior.compensate is not None:
                        prior.compensate(state)
                        compensated.append(prior.name)
                raise SagaFailed(step.name, exc, compensated) from exc
            done.append(step)
        return state
