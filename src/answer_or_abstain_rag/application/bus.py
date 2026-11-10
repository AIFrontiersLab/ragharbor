"""Message bus routing commands and queries to their handlers."""

from __future__ import annotations

from typing import Any, Callable

from answer_or_abstain_rag.kernel.errors import ConfigurationError


class MessageBus:
    def __init__(self) -> None:
        self._handlers: dict[type, Callable[[Any], Any]] = {}

    def register(self, message_type: type, handler: Callable[[Any], Any]) -> None:
        self._handlers[message_type] = handler

    def handle(self, message: Any) -> Any:
        handler = self._handlers.get(type(message))
        if handler is None:
            raise ConfigurationError(f"no handler registered for {type(message).__name__}")
        return handler(message)
