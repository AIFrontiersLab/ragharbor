"""JSON structured logging with run-scoped context fields."""

from __future__ import annotations

import json
import logging

_CONFIGURED = False


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = getattr(record, "fields", None)
        if isinstance(extra, dict):
            payload.update(extra)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, sort_keys=True)


def configure(level: str = "INFO") -> None:
    global _CONFIGURED
    root = logging.getLogger("answer_or_abstain_rag")
    root.setLevel(level.upper())
    if not _CONFIGURED:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        root.addHandler(handler)
        root.propagate = False
        _CONFIGURED = True


def get_logger(name: str) -> logging.LoggerAdapter:
    return _FieldsAdapter(logging.getLogger(f"answer_or_abstain_rag.{name}"), {})


class _FieldsAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        fields = dict(self.extra)
        fields.update(kwargs.pop("fields", {}) or {})
        kwargs["extra"] = {"fields": fields}
        return msg, kwargs

    def bind(self, **fields) -> "_FieldsAdapter":
        merged = dict(self.extra)
        merged.update(fields)
        return _FieldsAdapter(self.logger, merged)
