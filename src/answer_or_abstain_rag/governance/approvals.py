"""Human-in-the-loop approvals for high-risk runs."""

from __future__ import annotations

import hmac
from hashlib import sha256

from answer_or_abstain_rag.kernel.errors import NotFound


class ApprovalService:
    def __init__(self, secret: str = "local-development-secret") -> None:
        self._secret = secret.encode("utf-8")
        self._pending: dict[str, dict] = {}
        self._approved: dict[str, str] = {}

    def request(self, run_id: str, *, risk: float, reason: str) -> dict:
        ticket = {"run_id": run_id, "risk": round(risk, 3), "reason": reason, "status": "pending"}
        self._pending[run_id] = ticket
        return ticket

    def approve(self, run_id: str, approver: str) -> str:
        if run_id not in self._pending:
            raise NotFound(f"no pending approval for run {run_id}")
        self._pending[run_id]["status"] = "approved"
        self._approved[run_id] = approver
        return self.token_for(run_id)

    def is_approved(self, run_id: str) -> bool:
        return run_id in self._approved

    def token_for(self, run_id: str) -> str:
        return hmac.new(self._secret, run_id.encode("utf-8"), sha256).hexdigest()[:32]

    def pending(self) -> list[dict]:
        return [t for t in self._pending.values() if t["status"] == "pending"]
