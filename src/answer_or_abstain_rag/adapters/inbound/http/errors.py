"""Map domain errors onto HTTP status codes and a stable error body."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.errors import DomainError

STATUS_TEXT = {
    200: "200 OK",
    202: "202 Accepted",
    400: "400 Bad Request",
    403: "403 Forbidden",
    404: "404 Not Found",
    405: "405 Method Not Allowed",
    409: "409 Conflict",
    429: "429 Too Many Requests",
    500: "500 Internal Server Error",
    503: "503 Service Unavailable",
}


def status_line(code: int) -> str:
    return STATUS_TEXT.get(code, f"{code} Unknown")


def error_body(exc: Exception, *, request_id: str) -> tuple[int, dict]:
    if isinstance(exc, DomainError):
        return exc.http_status, {"error": exc.to_dict(), "request_id": request_id}
    return 500, {"error": {"code": "internal_error", "message": "unexpected error", "details": {}}, "request_id": request_id}
