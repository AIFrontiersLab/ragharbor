"""Cross-cutting HTTP concerns: request ids, per-tenant rate limiting, access logs."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.errors import BudgetExceeded
from answer_or_abstain_rag.kernel.ids import new_id
from answer_or_abstain_rag.observability.logging import get_logger

log = get_logger("http")


def request_id(environ: dict) -> str:
    supplied = environ.get("HTTP_X_REQUEST_ID", "")
    return supplied if supplied and len(supplied) <= 64 else new_id("req")


def enforce_rate_limit(limiter, environ: dict) -> None:
    tenant = environ.get("HTTP_X_TENANT", "default")
    if not limiter.allow(tenant):
        raise BudgetExceeded("rate limit exceeded", details={"tenant": tenant})


def access_log(method: str, path: str, status: int, rid: str, duration_ms: float) -> None:
    log.info(
        "request",
        fields={"method": method, "path": path, "status": status, "request_id": rid, "duration_ms": round(duration_ms, 3)},
    )
