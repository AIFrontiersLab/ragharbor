"""Minimal in-process tracer producing nested spans (OpenTelemetry-shaped, dependency-free)."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field

from answer_or_abstain_rag.kernel.clock import Clock, SystemClock
from answer_or_abstain_rag.kernel.ids import new_id


@dataclass
class Span:
    name: str
    trace_id: str
    span_id: str
    parent_id: str | None
    start: float
    end: float | None = None
    attributes: dict = field(default_factory=dict)
    status: str = "ok"

    @property
    def duration_ms(self) -> float:
        return 0.0 if self.end is None else (self.end - self.start) * 1000.0


class Tracer:
    def __init__(self, clock: Clock | None = None, *, max_spans: int = 10_000) -> None:
        self.clock = clock or SystemClock()
        self.spans: list[Span] = []
        self._stack: list[Span] = []
        self.max_spans = max_spans

    @contextmanager
    def span(self, name: str, **attributes):
        parent = self._stack[-1] if self._stack else None
        span = Span(
            name=name,
            trace_id=parent.trace_id if parent else new_id("trace"),
            span_id=new_id("span"),
            parent_id=parent.span_id if parent else None,
            start=self.clock.monotonic(),
            attributes=dict(attributes),
        )
        self._stack.append(span)
        try:
            yield span
        except Exception:
            span.status = "error"
            raise
        finally:
            span.end = self.clock.monotonic()
            self._stack.pop()
            self.spans.append(span)
            if len(self.spans) > self.max_spans:
                del self.spans[: len(self.spans) - self.max_spans]

    def for_trace(self, trace_id: str) -> list[Span]:
        return [s for s in self.spans if s.trace_id == trace_id]
