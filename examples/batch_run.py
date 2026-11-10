"""Run every example request and print a summary table."""

import json
from pathlib import Path

from answer_or_abstain_rag import build_container
from answer_or_abstain_rag.application.commands import RunPipeline

container = build_container()
for path in sorted((Path(__file__).parent / "requests").glob("*.json")):
    result = container.bus.handle(RunPipeline(request=json.loads(path.read_text())))
    cited = (result["answer"] or {}).get("evidence_ids", [])
    print(f"{path.stem:<22} {result['status']:<18} degraded={result['degraded']!s:<5} cited={cited}")
