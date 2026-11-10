"""Synchronous in-process event bus. Subscriber errors are isolated per handler."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable

from answer_or_abstain_rag.kernel.events import DomainEvent


class InMemoryEventBus:
    def __init__(self, history: int = 5000) -> None:
        self._subs: dict[str, list[Callable[[DomainEvent], None]]] = defaultdict(list)
        self.published: list[DomainEvent] = []
        self.dead_letters: list[dict] = []
        self.history = history

    def subscribe(self, name: str, handler: Callable[[DomainEvent], None]) -> None:
        self._subs[name].append(handler)

    def publish(self, event: DomainEvent) -> None:
        self.published.append(event)
        if len(self.published) > self.history:
            del self.published[: len(self.published) - self.history]
        for handler in self._subs.get(event.name, []) + self._subs.get("*", []):
            try:
                handler(event)
            except Exception as exc:  # noqa: BLE001
                self.dead_letters.append({"event": event.to_dict(), "error": str(exc)})

    def names(self) -> list[str]:
        return [e.name for e in self.published]
