"""Composable specifications (predicate objects) used by policies and filters."""

from __future__ import annotations

from typing import Any, Callable


class Specification:
    def __init__(self, predicate: Callable[[Any], bool], name: str = "spec") -> None:
        self._predicate = predicate
        self.name = name

    def is_satisfied_by(self, candidate: Any) -> bool:
        return bool(self._predicate(candidate))

    def __and__(self, other: "Specification") -> "Specification":
        return Specification(lambda c: self.is_satisfied_by(c) and other.is_satisfied_by(c), f"({self.name} & {other.name})")

    def __or__(self, other: "Specification") -> "Specification":
        return Specification(lambda c: self.is_satisfied_by(c) or other.is_satisfied_by(c), f"({self.name} | {other.name})")

    def __invert__(self) -> "Specification":
        return Specification(lambda c: not self.is_satisfied_by(c), f"~{self.name}")

    def __repr__(self) -> str:
        return f"Specification({self.name})"


ALWAYS = Specification(lambda _c: True, "always")
NEVER = Specification(lambda _c: False, "never")
