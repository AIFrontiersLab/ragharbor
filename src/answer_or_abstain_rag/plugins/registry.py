"""Stage factory registry. Components and third-party plugins register here by name."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from answer_or_abstain_rag.kernel.errors import ConfigurationError
from answer_or_abstain_rag.stages.base import Stage, StageServices

StageFactory = Callable[[StageServices], Stage]


@dataclass(frozen=True)
class Registration:
    name: str
    role: str
    factory: StageFactory
    source: str = "builtin"


class StageRegistry:
    def __init__(self) -> None:
        self._entries: dict[str, Registration] = {}

    def register(self, name: str, role: str, factory: StageFactory, *, source: str = "builtin", replace: bool = False) -> None:
        if name in self._entries and not replace:
            raise ConfigurationError(f"stage '{name}' is already registered")
        self._entries[name] = Registration(name=name, role=role, factory=factory, source=source)

    def create(self, name: str, services: StageServices) -> Stage:
        entry = self._entries.get(name)
        if entry is None:
            raise ConfigurationError(f"unknown stage '{name}'", details={"known": sorted(self._entries)})
        return entry.factory(services)

    def build(self, names: list[str], services: StageServices) -> list[Stage]:
        return [self.create(name, services) for name in names]

    def names(self) -> list[str]:
        return sorted(self._entries)

    def describe(self) -> list[dict]:
        return [{"name": e.name, "role": e.role, "source": e.source} for e in self._entries.values()]

    def __contains__(self, name: str) -> bool:
        return name in self._entries
