from answer_or_abstain_rag.plugins.registry import StageRegistry
from answer_or_abstain_rag.stage_catalog import BUILTINS, COMPONENTS, DEFAULT_STAGE_ORDER, register_all


def test_default_order_is_fully_registered():
    registry = StageRegistry()
    register_all(registry)
    for name in DEFAULT_STAGE_ORDER:
        assert name in registry


def test_every_component_is_in_the_catalog():
    registry = StageRegistry()
    register_all(registry)
    for comp in COMPONENTS:
        assert comp["slug"] in registry


def test_pipeline_starts_with_ingest_and_ends_with_answer():
    roles = {**BUILTINS, **{c["slug"]: c["role"] for c in COMPONENTS}}
    assert roles[DEFAULT_STAGE_ORDER[0]] == "ingest"
    assert roles[DEFAULT_STAGE_ORDER[-1]] == "answer"
    assert "policy" in {roles[s] for s in DEFAULT_STAGE_ORDER}
