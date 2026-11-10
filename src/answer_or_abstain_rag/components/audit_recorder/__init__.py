"""Audit Recorder.

Writes a hash-chainable audit record for every run, including denials and degradations.
"""

from answer_or_abstain_rag.components.audit_recorder.adapter import ROLE, build
from answer_or_abstain_rag.components.audit_recorder.config import CONFIG, AuditRecorderConfig
from answer_or_abstain_rag.components.audit_recorder.errors import AuditRecorderError
from answer_or_abstain_rag.components.audit_recorder.service import AuditRecorderService

__all__ = ["CONFIG", "ROLE", "build", "AuditRecorderConfig", "AuditRecorderError", "AuditRecorderService"]
