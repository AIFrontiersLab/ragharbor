"""Lifecycle hooks around stage execution. Hook failures are isolated and recorded."""

from __future__ import annotations

from typing import Callable

Hook = Callable[..., None]


class HookManager:
    PHASES = ("before_stage", "after_stage", "on_error", "on_complete")

    def __init__(self) -> None:
        self._hooks: dict[str, list[Hook]] = {phase: [] for phase in self.PHASES}
        self.failures: list[dict] = []

    def add(self, phase: str, hook: Hook) -> None:
        if phase not in self._hooks:
            raise ValueError(f"unknown hook phase: {phase}")
        self._hooks[phase].append(hook)

    def fire(self, phase: str, **kwargs) -> None:
        for hook in self._hooks.get(phase, []):
            try:
                hook(**kwargs)
            except Exception as exc:  # noqa: BLE001 - hooks must never break a run
                self.failures.append({"phase": phase, "hook": getattr(hook, "__name__", repr(hook)), "error": str(exc)})
