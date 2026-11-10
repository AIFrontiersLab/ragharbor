"""Data-driven scenarios in tests/fixtures/scenarios.json."""

import json
from pathlib import Path

import pytest

from answer_or_abstain_rag.application.commands import RunPipeline

SCENARIOS = json.loads((Path(__file__).parents[1] / "fixtures" / "scenarios.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["name"] for s in SCENARIOS])
def test_scenario(scenario, container):
    roles = {s.role for s in container.stages}
    required = scenario.get("requires_role")
    if required and required not in roles:
        pytest.skip(f"pipeline has no {required} stage")
    result = container.bus.handle(RunPipeline(request=scenario["request"]))
    expect = scenario["expect"]
    if "status" in expect:
        assert result["status"] == expect["status"]
    if "abstain_reason" in expect:
        assert result["abstain_reason"] == expect["abstain_reason"]
    cited = (result.get("answer") or {}).get("evidence_ids", [])
    if "min_citations" in expect:
        assert len(cited) >= expect["min_citations"]
    for doc in expect.get("excluded", []):
        assert doc not in cited
    for doc in expect.get("included", []):
        assert doc in cited
