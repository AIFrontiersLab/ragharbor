"""Token-bucket rate limiting, optionally keyed per tenant."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.clock import Clock, SystemClock


class TokenBucket:
    def __init__(self, rate_per_second: float, burst: int, *, clock: Clock | None = None) -> None:
        self.rate = float(rate_per_second)
        self.capacity = float(burst)
        self.clock = clock or SystemClock()
        self._tokens = float(burst)
        self._last = self.clock.monotonic()

    def _refill(self) -> None:
        now = self.clock.monotonic()
        self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.rate)
        self._last = now

    def try_acquire(self, tokens: float = 1.0) -> bool:
        self._refill()
        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        return False

    @property
    def available(self) -> float:
        self._refill()
        return self._tokens


class KeyedRateLimiter:
    def __init__(self, rate_per_second: float, burst: int, *, clock: Clock | None = None) -> None:
        self.rate = rate_per_second
        self.burst = burst
        self.clock = clock or SystemClock()
        self._buckets: dict[str, TokenBucket] = {}

    def allow(self, key: str) -> bool:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = self._buckets[key] = TokenBucket(self.rate, self.burst, clock=self.clock)
        return bucket.try_acquire()
