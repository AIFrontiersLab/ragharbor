import pytest

from answer_or_abstain_rag.kernel.errors import ConfigurationError, InvalidTransition
from answer_or_abstain_rag.plugins.hooks import HookManager
from answer_or_abstain_rag.plugins.registry import StageRegistry
from answer_or_abstain_rag.stages.enrich import EnrichStage
from answer_or_abstain_rag.workflows.checkpoint import CheckpointStore
from answer_or_abstain_rag.workflows.saga import Saga, SagaFailed, SagaStep
from answer_or_abstain_rag.workflows.state_machine import RunState, RunStateMachine

# --- test_hooks.py ---------------------------------------------------------

def test_hooks_fire_and_failures_are_isolated():
    hooks = HookManager()
    seen = []
    hooks.add("before_stage", lambda **kw: seen.append(kw["n"]))
    hooks.add("before_stage", lambda **kw: 1 / 0)
    hooks.fire("before_stage", n=1)
    assert seen == [1]
    assert hooks.failures[0]["phase"] == "before_stage"


def test_unknown_phase_rejected():
    with pytest.raises(ValueError):
        HookManager().add("whenever", lambda: None)


# --- test_registry.py ------------------------------------------------------

def test_register_create_and_duplicates(services):
    reg = StageRegistry()
    reg.register("x", "enrich", lambda s: EnrichStage("x", s))
    assert reg.create("x", services).name == "x"
    with pytest.raises(ConfigurationError):
        reg.register("x", "enrich", lambda s: EnrichStage("x", s))
    reg.register("x", "enrich", lambda s: EnrichStage("x2", s), replace=True)
    assert reg.create("x", services).name == "x2"


def test_unknown_stage_lists_known(services):
    reg = StageRegistry()
    reg.register("a", "enrich", lambda s: EnrichStage("a", s))
    with pytest.raises(ConfigurationError) as info:
        reg.create("b", services)
    assert info.value.details["known"] == ["a"]


# --- test_checkpoint.py ----------------------------------------------------

def test_save_load_and_eviction():
    store = CheckpointStore(max_runs=2)
    store.save("r1", "a", {"status": "ok"})
    store.save("r1", "b", {"status": "ok"})
    assert store.last_completed("r1") == "b"
    store.save("r2", "a", {})
    store.save("r3", "a", {})
    assert store.load("r1") == []
    assert store.last_completed("missing") is None


# --- test_saga.py ----------------------------------------------------------

def test_compensates_completed_steps_in_reverse():
    log = []

    def fail(state):
        raise RuntimeError("nope")

    saga = Saga(
        [
            SagaStep("one", lambda s: log.append("one"), lambda s: log.append("undo-one")),
            SagaStep("two", lambda s: log.append("two"), lambda s: log.append("undo-two")),
            SagaStep("three", fail),
        ]
    )
    with pytest.raises(SagaFailed) as info:
        saga.execute({})
    assert log == ["one", "two", "undo-two", "undo-one"]
    assert info.value.compensated == ["two", "one"]


def test_success_returns_state():
    assert Saga([SagaStep("a", lambda s: s.update(x=1))]).execute({}) == {"x": 1}


# --- test_state_machine.py -------------------------------------------------

def test_legal_path():
    m = RunStateMachine()
    m.transition(RunState.RUNNING)
    m.transition(RunState.AWAITING_APPROVAL)
    m.transition(RunState.RUNNING)
    m.transition(RunState.COMPLETED)
    assert m.terminal and m.history[0] is RunState.PENDING


def test_terminal_states_are_final():
    m = RunStateMachine(RunState.COMPLETED)
    with pytest.raises(InvalidTransition):
        m.transition(RunState.RUNNING)
