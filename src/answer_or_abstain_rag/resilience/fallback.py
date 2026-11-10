"""Functional fallback helper used by adapters that wrap optional dependencies."""

from __future__ import annotations

from typing import Callable, TypeVar

T = TypeVar("T")


def with_fallback(primary: Callable[[], T], fallback: Callable[[Exception], T], *, catch: tuple = (Exception,)) -> T:
    try:
        return primary()
    except catch as exc:  # type: ignore[misc]
        return fallback(exc)
