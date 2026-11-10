import pytest

from answer_or_abstain_rag.kernel.clock import FakeClock
from answer_or_abstain_rag.kernel.errors import CircuitOpenError, StageError
from answer_or_abstain_rag.resilience.bulkhead import Bulkhead
from answer_or_abstain_rag.resilience.circuit_breaker import BreakerState, CircuitBreaker
from answer_or_abstain_rag.resilience.fallback import with_fallback
from answer_or_abstain_rag.resilience.rate_limiter import KeyedRateLimiter, TokenBucket
from answer_or_abstain_rag.resilience.retry import RetryPolicy
from answer_or_abstain_rag.resilience.timeout import Deadline

# --- test_bulkhead.py ------------------------------------------------------

def test_rejects_beyond_limit_and_releases():
    bulkhead = Bulkhead("p", 1)
    with bulkhead.slot():
        assert bulkhead.in_flight == 1
        with pytest.raises(StageError):
            with bulkhead.slot():
                pass
    assert bulkhead.in_flight == 0


# --- test_circuit_breaker.py -----------------------------------------------

def _boom():
    raise RuntimeError("down")


def test_opens_after_threshold_and_half_opens_after_reset():
    clock = FakeClock()
    breaker = CircuitBreaker("s", failure_threshold=2, reset_seconds=10, clock=clock)
    for _ in range(2):
        with pytest.raises(RuntimeError):
            breaker.call(_boom)
    assert breaker.state is BreakerState.OPEN
    with pytest.raises(CircuitOpenError):
        breaker.call(lambda: 1)
    clock.advance(10)
    assert breaker.state is BreakerState.HALF_OPEN
    assert breaker.call(lambda: 42) == 42
    assert breaker.state is BreakerState.CLOSED


def test_half_open_failure_reopens_immediately():
    clock = FakeClock()
    breaker = CircuitBreaker("s", failure_threshold=1, reset_seconds=5, clock=clock)
    with pytest.raises(RuntimeError):
        breaker.call(_boom)
    clock.advance(5)
    with pytest.raises(RuntimeError):
        breaker.call(_boom)
    assert breaker.state is BreakerState.OPEN
    assert breaker.snapshot()["state"] == "open"


# --- test_deadline.py ------------------------------------------------------

def test_deadline_tracks_elapsed_time():
    clock = FakeClock()
    deadline = Deadline(100, clock=clock)
    clock.advance(0.05)
    assert round(deadline.remaining_ms()) == 50
    assert not deadline.expired()
    clock.advance(0.06)
    assert deadline.expired()


# --- test_fallback_helper.py -----------------------------------------------

def test_with_fallback():
    assert with_fallback(lambda: 1, lambda e: 2) == 1
    assert with_fallback(lambda: 1 / 0, lambda e: type(e).__name__) == "ZeroDivisionError"


# --- test_rate_limiter.py --------------------------------------------------

def test_token_bucket_refills_over_time():
    clock = FakeClock()
    bucket = TokenBucket(rate_per_second=2, burst=2, clock=clock)
    assert bucket.try_acquire() and bucket.try_acquire()
    assert not bucket.try_acquire()
    clock.advance(0.5)
    assert bucket.try_acquire()


def test_keys_are_isolated():
    limiter = KeyedRateLimiter(0, 1, clock=FakeClock())
    assert limiter.allow("a") and not limiter.allow("a")
    assert limiter.allow("b")


# --- test_retry.py ---------------------------------------------------------

def test_retries_retryable_errors_with_backoff():
    clock = FakeClock()
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise StageError("s", "flaky", retryable=True)
        return "ok"

    assert RetryPolicy(attempts=2, base_delay=0.1, clock=clock).call(flaky) == "ok"
    assert clock.sleeps == [0.1, 0.2]


def test_does_not_retry_non_retryable():
    calls = {"n": 0}

    def fatal():
        calls["n"] += 1
        raise StageError("s", "fatal", retryable=False)

    with pytest.raises(StageError):
        RetryPolicy(attempts=5, clock=FakeClock()).call(fatal)
    assert calls["n"] == 1


def test_delay_cap():
    assert RetryPolicy(attempts=4, base_delay=1, max_delay=3).delays() == [1, 2, 3, 3]
