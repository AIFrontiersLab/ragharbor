"""WSGI application exposing the pipeline over HTTP.

Endpoints
---------
GET  /healthz                 liveness
GET  /readyz                  readiness (dependency checks)
GET  /metrics                 Prometheus exposition
GET  /v1/pipeline             stage topology
POST /v1/runs                 execute a run
GET  /v1/runs                 list recent runs
GET  /v1/runs/{run_id}        fetch one run
POST /v1/runs/{run_id}/approve  approve a run awaiting approval
"""

from __future__ import annotations

import json
import time

from answer_or_abstain_rag.adapters.inbound.http import middleware
from answer_or_abstain_rag.adapters.inbound.http.errors import error_body, status_line
from answer_or_abstain_rag.adapters.inbound.http.routes import Router
from answer_or_abstain_rag.adapters.inbound.http.schemas import envelope, read_json
from answer_or_abstain_rag.application.commands import ApproveRun, RunPipeline
from answer_or_abstain_rag.application.queries import DescribePipeline, GetRun, ListRuns
from answer_or_abstain_rag.kernel.errors import DomainError


class HttpApp:
    def __init__(self, container) -> None:
        self.c = container
        self.router = Router()
        self.router.add("GET", "/healthz", self.healthz)
        self.router.add("GET", "/readyz", self.readyz)
        self.router.add("GET", "/metrics", self.metrics)
        self.router.add("GET", "/v1/pipeline", self.pipeline)
        self.router.add("POST", "/v1/runs", self.create_run)
        self.router.add("GET", "/v1/runs", self.list_runs)
        self.router.add("GET", "/v1/runs/{run_id}", self.get_run)
        self.router.add("POST", "/v1/runs/{run_id}/approve", self.approve_run)

    # WSGI entry point -------------------------------------------------------
    def __call__(self, environ, start_response):
        started = time.perf_counter()
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/") or "/"
        rid = middleware.request_id(environ)
        try:
            handler, params, exists = self.router.match(method, path)
            if handler is None:
                code = 405 if exists else 404
                body = {"error": {"code": "method_not_allowed" if exists else "not_found", "message": path, "details": {}}, "request_id": rid}
                return self._respond(start_response, code, body, rid, method, path, started)
            if method == "POST":
                middleware.enforce_rate_limit(self.c.rate_limiter, environ)
            code, payload = handler(environ, **params)
            if isinstance(payload, str):
                return self._respond_text(start_response, code, payload, rid, method, path, started)
            return self._respond(start_response, code, envelope(payload, request_id=rid), rid, method, path, started)
        except Exception as exc:  # noqa: BLE001 - translated to an HTTP error
            if not isinstance(exc, DomainError):
                middleware.log.exception("unhandled error", fields={"request_id": rid})
            code, body = error_body(exc, request_id=rid)
            return self._respond(start_response, code, body, rid, method, path, started)

    # Handlers ---------------------------------------------------------------
    def healthz(self, environ):
        return 200, {"status": "ok"}

    def readyz(self, environ):
        report = self.c.health.run()
        return (200 if report["ok"] else 503), report

    def metrics(self, environ):
        return 200, self.c.metrics.render_prometheus()

    def pipeline(self, environ):
        return 200, self.c.bus.handle(DescribePipeline())

    def create_run(self, environ):
        body = read_json(environ)
        result = self.c.bus.handle(RunPipeline(request=body))
        return (202 if result["status"] == "awaiting_approval" else 200), result

    def list_runs(self, environ):
        return 200, self.c.bus.handle(ListRuns())

    def get_run(self, environ, run_id: str):
        return 200, self.c.bus.handle(GetRun(run_id=run_id))

    def approve_run(self, environ, run_id: str):
        body = read_json(environ)
        command = ApproveRun(
            run_id=run_id,
            approver=str(body.get("approver") or "unknown"),
            principal=body.get("principal") or {"subject": "anonymous", "roles": ["guest"]},
        )
        return 200, self.c.bus.handle(command)

    # Helpers ----------------------------------------------------------------
    def _respond(self, start_response, code, body, rid, method, path, started):
        raw = json.dumps(body, default=str).encode("utf-8")
        headers = [("Content-Type", "application/json"), ("Content-Length", str(len(raw))), ("X-Request-Id", rid)]
        start_response(status_line(code), headers)
        middleware.access_log(method, path, code, rid, (time.perf_counter() - started) * 1000)
        return [raw]

    def _respond_text(self, start_response, code, text, rid, method, path, started):
        raw = text.encode("utf-8")
        headers = [("Content-Type", "text/plain; version=0.0.4"), ("Content-Length", str(len(raw))), ("X-Request-Id", rid)]
        start_response(status_line(code), headers)
        middleware.access_log(method, path, code, rid, (time.perf_counter() - started) * 1000)
        return [raw]


def serve(container, host: str, port: int) -> None:  # pragma: no cover - blocking server
    from wsgiref.simple_server import make_server

    with make_server(host, port, HttpApp(container)) as server:
        print(f"listening on http://{host}:{port}")
        server.serve_forever()
