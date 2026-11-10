"""Core entities for Answer-or-Abstain RAG.

``Request`` enters, flows through a ``PipelineContext`` mutated by stages, and
leaves as an ``Outcome``. The context is the only mutable object; stages own no
hidden state about a run.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from answer_or_abstain_rag.kernel.errors import ValidationError

MAX_QUERY_CHARS = 4000


@dataclass(frozen=True)
class Principal:
    subject: str = "anonymous"
    roles: tuple[str, ...] = ("reader",)
    groups: tuple[str, ...] = ()
    tenant: str = "default"

    @classmethod
    def from_dict(cls, data: dict | None, *, tenant: str) -> "Principal":
        data = data or {}
        return cls(
            subject=str(data.get("subject") or "anonymous"),
            roles=tuple(str(r) for r in (data.get("roles") or ["reader"])),
            groups=tuple(str(g) for g in (data.get("groups") or [])),
            tenant=str(data.get("tenant") or tenant),
        )


@dataclass
class Candidate:
    doc_id: str
    text: str = ""
    prior_score: float = 0.0
    score: float = 0.0
    classification: str = "internal"
    acl: tuple[str, ...] = ()
    metadata: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Candidate":
        if not isinstance(data, dict) or not data.get("doc_id"):
            raise ValidationError("each candidate requires a doc_id")
        prior = float(data.get("score", data.get("prior_score", 0.0)) or 0.0)
        return cls(
            doc_id=str(data["doc_id"]),
            text=str(data.get("text") or ""),
            prior_score=prior,
            score=prior,
            classification=str(data.get("classification") or "internal").lower(),
            acl=tuple(str(a) for a in (data.get("acl") or [])),
            metadata=dict(data.get("metadata") or {}),
        )

    def to_dict(self) -> dict:
        out = asdict(self)
        out["acl"] = list(self.acl)
        return out


@dataclass(frozen=True)
class Request:
    query: str
    tenant: str = "default"
    principal: Principal = field(default_factory=Principal)
    candidates: tuple[Candidate, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    budget_tokens: int | None = None
    require_evidence: bool = True
    top_k: int | None = None
    options: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Request":
        if not isinstance(data, dict):
            raise ValidationError("request body must be a JSON object")
        query = data.get("query")
        if not isinstance(query, str) or not query.strip():
            raise ValidationError("query must be a non-empty string")
        if len(query) > MAX_QUERY_CHARS:
            raise ValidationError(f"query exceeds {MAX_QUERY_CHARS} characters")
        tenant = str(data.get("tenant") or "default")
        raw_candidates = data.get("candidates") or []
        if not isinstance(raw_candidates, list):
            raise ValidationError("candidates must be a list")
        budget = data.get("budget_tokens")
        if budget is not None and (not isinstance(budget, int) or budget < 0):
            raise ValidationError("budget_tokens must be a non-negative integer")
        top_k = data.get("top_k")
        if top_k is not None and (not isinstance(top_k, int) or top_k < 1):
            raise ValidationError("top_k must be a positive integer")
        return cls(
            query=query.strip(),
            tenant=tenant,
            principal=Principal.from_dict(data.get("principal"), tenant=tenant),
            candidates=tuple(Candidate.from_dict(c) for c in raw_candidates),
            evidence_ids=tuple(str(e) for e in (data.get("evidence_ids") or [])),
            budget_tokens=budget,
            require_evidence=bool(data.get("require_evidence", True)),
            top_k=top_k,
            options=dict(data.get("options") or {}),
        )


@dataclass(frozen=True)
class Citation:
    doc_id: str
    score: float
    snippet: str = ""


@dataclass
class Answer:
    text: str
    citations: list[Citation] = field(default_factory=list)

    @property
    def evidence_ids(self) -> list[str]:
        return [c.doc_id for c in self.citations]

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "evidence_ids": self.evidence_ids,
            "citations": [asdict(c) for c in self.citations],
        }


@dataclass
class StageEvent:
    stage: str
    status: str = "ok"
    duration_ms: float = 0.0
    detail: dict = field(default_factory=dict)


@dataclass
class PipelineContext:
    run_id: str
    request: Request
    candidates: list[Candidate] = field(default_factory=list)
    events: list[StageEvent] = field(default_factory=list)
    decisions: list[dict] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    degraded: bool = False
    cache_hit: bool = False
    tokens_used: int = 0
    answer: Answer | None = None
    abstain_reason: str | None = None
    halted: bool = False
    metadata: dict = field(default_factory=dict)

    def decide(self, stage: str, action: str, **detail) -> None:
        self.decisions.append({"stage": stage, "action": action, **detail})

    def abstain(self, reason: str) -> None:
        self.abstain_reason = reason
        self.answer = None
        self.halted = True


@dataclass
class Outcome:
    run_id: str
    status: str
    query: str
    answer: Answer | None
    abstain_reason: str | None
    degraded: bool
    cache_hit: bool
    events: list[StageEvent]
    decisions: list[dict]
    errors: list[dict]
    tokens_used: int
    concept_id: int = 40
    concept_name: str = "Answer-or-Abstain RAG"

    @property
    def abstain(self) -> bool:
        return self.answer is None

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "query": self.query,
            "abstain": self.abstain,
            "abstain_reason": self.abstain_reason,
            "answer": self.answer.to_dict() if self.answer else None,
            "degraded": self.degraded,
            "cache_hit": self.cache_hit,
            "tokens_used": self.tokens_used,
            "events": [asdict(e) for e in self.events],
            "decisions": list(self.decisions),
            "errors": list(self.errors),
            "concept_id": self.concept_id,
            "concept_name": self.concept_name,
        }
