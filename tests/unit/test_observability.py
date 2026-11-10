import json
import logging

import pytest

from answer_or_abstain_rag.kernel.clock import FakeClock
from answer_or_abstain_rag.observability.audit import chain, verify_chain
from answer_or_abstain_rag.observability.health import HealthRegistry
from answer_or_abstain_rag.observability.logging import JsonFormatter, get_logger
from answer_or_abstain_rag.observability.metrics import MetricsRegistry
from answer_or_abstain_rag.observability.tracing import Tracer

# --- test_audit_chain.py ---------------------------------------------------

def test_chain_detects_tampering():
    chained = chain([{"a": 1}, {"b": 2}, {"c": 3}])
    assert verify_chain(chained)
    chained[1]["b"] = 99
    assert not verify_chain(chained)


def test_chain_detects_deletion():
    chained = chain([{"a": 1}, {"b": 2}, {"c": 3}])
    del chained[1]
    assert not verify_chain(chained)


# --- test_health.py --------------------------------------------------------

def test_failing_and_raising_checks_reported():
    health = HealthRegistry()
    health.register("ok", lambda: True)
    health.register("bad", lambda: False)
    health.register("boom", lambda: 1 / 0)
    report = health.run()
    assert report == {"ok": False, "checks": {"ok": True, "bad": False, "boom": False}}


# --- test_logging.py -------------------------------------------------------

def test_json_formatter_includes_bound_fields():
    record = logging.LogRecord("x", logging.INFO, __file__, 1, "hello", None, None)
    record.fields = {"run_id": "r1"}
    payload = json.loads(JsonFormatter().format(record))
    assert payload["message"] == "hello" and payload["run_id"] == "r1"


def test_bind_merges_fields():
    log = get_logger("t").bind(run_id="r1")
    msg, kwargs = log.process("m", {"fields": {"stage": "s"}})
    assert kwargs["extra"]["fields"] == {"run_id": "r1", "stage": "s"}


# --- test_metrics.py -------------------------------------------------------

def test_counters_histograms_and_exposition():
    m = MetricsRegistry(buckets=(10, float("inf")))
    m.inc("runs_total", status="ok")
    m.inc("runs_total", 2, status="ok")
    m.observe("latency_ms", 5)
    m.observe("latency_ms", 50)
    assert m.counter("runs_total", status="ok") == 3
    text = m.render_prometheus()
    assert 'runs_total{status="ok"} 3' in text
    assert 'latency_ms_bucket{le="10"} 1' in text
    assert 'latency_ms_bucket{le="+Inf"} 2' in text
    assert "latency_ms_count 2" in text


# --- test_tracing.py -------------------------------------------------------

def test_nested_spans_share_trace_and_record_errors():
    clock = FakeClock()
    tracer = Tracer(clock)
    with tracer.span("outer") as outer:
        clock.advance(0.01)
        with pytest.raises(ValueError):
            with tracer.span("inner"):
                raise ValueError("x")
    inner = next(s for s in tracer.spans if s.name == "inner")
    assert inner.parent_id == outer.span_id and inner.trace_id == outer.trace_id
    assert inner.status == "error"
    assert round(outer.duration_ms) == 10
    assert len(tracer.for_trace(outer.trace_id)) == 2
