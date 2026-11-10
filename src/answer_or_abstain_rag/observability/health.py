"""Liveness and readiness checks aggregated for the /healthz and /readyz endpoints."""

from __future__ import annotations

from typing import Callable


class HealthRegistry:
    def __init__(self) -> None:
        self._checks: dict[str, Callable[[], bool]] = {}

    def register(self, name: str, check: Callable[[], bool]) -> None:
        self._checks[name] = check

    def run(self) -> dict:
        results = {}
        for name, check in self._checks.items():
            try:
                results[name] = bool(check())
            except Exception:  # noqa: BLE001 - a failing check is reported, never raised
                results[name] = False
        return {"ok": all(results.values()) if results else True, "checks": results}
