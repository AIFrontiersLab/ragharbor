"""CLI command implementations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from answer_or_abstain_rag.application.commands import RunPipeline
from answer_or_abstain_rag.application.queries import DescribePipeline
from answer_or_abstain_rag.config.loader import load_settings
from answer_or_abstain_rag.container import build_container


def _container(args, **kwargs):
    return build_container(load_settings(args.config) if args.config else None, **kwargs)


def cmd_run(args):
    raw = sys.stdin.read() if args.request == "-" else Path(args.request).read_text(encoding="utf-8")
    corpus = None
    if getattr(args, "corpus", None):
        from answer_or_abstain_rag.adapters.outbound.memory_corpus import InMemoryCorpus

        corpus = InMemoryCorpus.from_json(args.corpus)
    container = _container(args, corpus=corpus)
    return container.bus.handle(RunPipeline(request=json.loads(raw)))


def cmd_serve(args):  # pragma: no cover - blocking
    from answer_or_abstain_rag.adapters.inbound.http.app import serve

    container = _container(args)
    http = container.settings.http
    serve(container, args.host or http.host, args.port or http.port)
    return None


def cmd_describe(args):
    return _container(args).bus.handle(DescribePipeline())


def cmd_config(args):
    return _container(args).settings.to_dict()


def cmd_doctor(args):
    report = _container(args).health.run()
    if not report["ok"]:
        raise RuntimeError(f"readiness failed: {report}")
    return report
