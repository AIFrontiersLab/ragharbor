"""HTTP adapter exercised through the WSGI interface (no sockets)."""

import io
import json

import pytest

from answer_or_abstain_rag.adapters.inbound.http.app import HttpApp


def call(app, method, path, body=None, headers=None):
    raw = json.dumps(body).encode() if body is not None else b""
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": str(len(raw)),
        "wsgi.input": io.BytesIO(raw),
    }
    for key, value in (headers or {}).items():
        environ["HTTP_" + key.upper().replace("-", "_")] = value
    captured = {}

    def start_response(status, response_headers):
        captured["status"] = int(status.split()[0])
        captured["headers"] = dict(response_headers)

    payload = b"".join(app(environ, start_response))
    ctype = captured["headers"]["Content-Type"]
    return captured["status"], (json.loads(payload) if ctype.startswith("application/json") else payload.decode()), captured["headers"]


@pytest.fixture
def app(container):
    return HttpApp(container)


def test_health_and_ready(app):
    assert call(app, "GET", "/healthz")[0] == 200
    status, body, _ = call(app, "GET", "/readyz")
    assert status == 200 and body["data"]["ok"]


def test_create_and_fetch_run(app, make_request):
    status, body, headers = call(app, "POST", "/v1/runs", make_request(), {"X-Request-Id": "req-1"})
    assert status == 200 and headers["X-Request-Id"] == "req-1"
    run_id = body["data"]["run_id"]
    status, fetched, _ = call(app, "GET", f"/v1/runs/{run_id}")
    assert status == 200 and fetched["data"]["run_id"] == run_id
    status, listed, _ = call(app, "GET", "/v1/runs")
    assert listed["data"][0]["run_id"] == run_id


def test_validation_errors_are_400(app):
    status, body, _ = call(app, "POST", "/v1/runs", {"query": ""})
    assert status == 400 and body["error"]["code"] == "validation_error"


def test_invalid_json_is_400(app):
    environ_body = b"{not json"
    environ = {"REQUEST_METHOD": "POST", "PATH_INFO": "/v1/runs", "CONTENT_LENGTH": str(len(environ_body)), "wsgi.input": io.BytesIO(environ_body)}
    statuses = []
    app(environ, lambda s, h: statuses.append(s))
    assert statuses[0].startswith("400")


def test_not_found_and_method_not_allowed(app):
    assert call(app, "GET", "/nope")[0] == 404
    assert call(app, "DELETE", "/v1/runs")[0] == 405
    assert call(app, "GET", "/v1/runs/run_missing")[0] == 404


def test_forbidden_role_is_403(app, make_request):
    status, body, _ = call(app, "POST", "/v1/runs", make_request(principal={"roles": ["nobody"]}))
    assert status == 403


def test_metrics_and_pipeline(app, make_request):
    call(app, "POST", "/v1/runs", make_request())
    status, text, headers = call(app, "GET", "/metrics")
    assert status == 200 and "pipeline_runs_total" in text
    status, body, _ = call(app, "GET", "/v1/pipeline")
    assert [s["name"] for s in body["data"]["stages"]]


def test_rate_limit_is_429(container, make_request):
    from answer_or_abstain_rag.resilience.rate_limiter import KeyedRateLimiter

    container.rate_limiter = KeyedRateLimiter(0, 1, clock=container.clock)
    app = HttpApp(container)
    assert call(app, "POST", "/v1/runs", make_request(), {"X-Tenant": "t"})[0] == 200
    assert call(app, "POST", "/v1/runs", make_request(), {"X-Tenant": "t"})[0] == 429
