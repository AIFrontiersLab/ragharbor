"""Counters and histograms with Prometheus text exposition."""

from __future__ import annotations

import threading
from collections import defaultdict

DEFAULT_BUCKETS = (1, 5, 10, 25, 50, 100, 250, 500, 1000, float("inf"))


def _key(name: str, labels: dict | None) -> tuple:
    return (name, tuple(sorted((labels or {}).items())))


class MetricsRegistry:
    def __init__(self, buckets: tuple = DEFAULT_BUCKETS) -> None:
        self._lock = threading.Lock()
        self._counters: dict[tuple, float] = defaultdict(float)
        self._hist: dict[tuple, list[float]] = defaultdict(list)
        self.buckets = buckets

    def inc(self, name: str, value: float = 1.0, **labels) -> None:
        with self._lock:
            self._counters[_key(name, labels)] += value

    def observe(self, name: str, value: float, **labels) -> None:
        with self._lock:
            self._hist[_key(name, labels)].append(float(value))

    def counter(self, name: str, **labels) -> float:
        return self._counters.get(_key(name, labels), 0.0)

    def histogram(self, name: str, **labels) -> list[float]:
        return list(self._hist.get(_key(name, labels), []))

    def render_prometheus(self) -> str:
        lines: list[str] = []
        with self._lock:
            for (name, labels), value in sorted(self._counters.items()):
                lines.append(f"{name}{_fmt(labels)} {value:g}")
            for (name, labels), values in sorted(self._hist.items()):
                for bound in self.buckets:
                    count = sum(1 for v in values if v <= bound)
                    le = "+Inf" if bound == float("inf") else f"{bound:g}"
                    lines.append(f"{name}_bucket{_fmt(labels + (('le', le),))} {count}")
                lines.append(f"{name}_count{_fmt(labels)} {len(values)}")
                lines.append(f"{name}_sum{_fmt(labels)} {sum(values):g}")
        return "\n".join(lines) + "\n"


def _fmt(labels: tuple) -> str:
    if not labels:
        return ""
    return "{" + ",".join(f'{k}="{v}"' for k, v in labels) + "}"
