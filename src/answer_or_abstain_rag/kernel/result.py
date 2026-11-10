"""A small Result type for explicit success/failure flows.

Stages and handlers return ``Result`` values instead of raising for expected
failures (validation, policy denials). Exceptions are reserved for defects and
infrastructure faults that the resilience layer is designed to absorb.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def map(self, fn: Callable[[T], U]) -> "Ok[U]":
        return Ok(fn(self.value))

    def bind(self, fn: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        return fn(self.value)

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def map(self, fn: Callable) -> "Err[E]":
        return self

    def bind(self, fn: Callable) -> "Err[E]":
        return self

    def unwrap(self):
        raise RuntimeError(f"called unwrap() on Err: {self.error!r}")

    def unwrap_or(self, default):
        return default


Result = Union[Ok[T], Err[E]]


def collect(results: list) -> "Result":
    """Return Ok(list of values) if every result is Ok, else the first Err."""
    values = []
    for item in results:
        if item.is_err():
            return item
        values.append(item.value)
    return Ok(values)
