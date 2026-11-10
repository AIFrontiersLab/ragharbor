"""Configuration model.

Defaults live here so the service starts with zero configuration. Profiles under
``config/*.toml`` and ``ANSWER_OR_ABSTAIN_RAG_*`` environment variables override them.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from answer_or_abstain_rag.stage_catalog import DEFAULT_STAGE_ORDER


@dataclass
class AppSettings:
    name: str = "answer-or-abstain-rag"
    environment: str = "development"
    log_level: str = "INFO"


@dataclass
class PipelineSettings:
    stages: list[str] = field(default_factory=lambda: list(DEFAULT_STAGE_ORDER))
    top_k: int = 10
    max_candidates: int = 200
    require_evidence: bool = True
    prior_weight: float = 0.4
    min_score: float = 0.0
    stage_timeout_ms: int = 250


@dataclass
class ResilienceSettings:
    breaker_failure_threshold: int = 3
    breaker_reset_seconds: float = 30.0
    retry_attempts: int = 2
    retry_base_delay: float = 0.0
    bulkhead_limit: int = 32
    rate_limit_per_second: float = 50.0
    rate_limit_burst: int = 100


@dataclass
class GovernanceSettings:
    default_clearance: str = "internal"
    redact_pii: bool = True
    approval_risk_threshold: float = 0.8
    role_clearances: dict = field(
        default_factory=lambda: {
            "reader": "internal",
            "analyst": "confidential",
            "admin": "restricted",
            "guest": "public",
        }
    )


@dataclass
class CacheSettings:
    enabled: bool = True
    capacity: int = 1024
    ttl_seconds: float = 300.0


@dataclass
class BudgetSettings:
    default_tokens: int = 4000
    hard_limit_tokens: int = 32000


@dataclass
class HttpSettings:
    host: str = "127.0.0.1"
    port: int = 8080


@dataclass
class StorageSettings:
    backend: str = "memory"
    path: str = "var/runs"


@dataclass
class Settings:
    app: AppSettings = field(default_factory=AppSettings)
    pipeline: PipelineSettings = field(default_factory=PipelineSettings)
    resilience: ResilienceSettings = field(default_factory=ResilienceSettings)
    governance: GovernanceSettings = field(default_factory=GovernanceSettings)
    cache: CacheSettings = field(default_factory=CacheSettings)
    budget: BudgetSettings = field(default_factory=BudgetSettings)
    http: HttpSettings = field(default_factory=HttpSettings)
    storage: StorageSettings = field(default_factory=StorageSettings)

    def to_dict(self) -> dict:
        return asdict(self)
