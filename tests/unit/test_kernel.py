import pytest

from answer_or_abstain_rag.kernel.clock import FakeClock, SystemClock
from answer_or_abstain_rag.kernel.errors import CircuitOpenError, PolicyViolation, StageError, ValidationError
from answer_or_abstain_rag.kernel.ids import new_id, stable_hash
from answer_or_abstain_rag.kernel.result import Err, Ok, collect
from answer_or_abstain_rag.kernel.specification import ALWAYS, NEVER, Specification
from answer_or_abstain_rag.kernel.text import estimate_tokens, normalize, snippet, tokenize

# --- test_clock.py ---------------------------------------------------------

def test_fake_clock_advances_and_records_sleeps():
    clock = FakeClock()
    clock.sleep(1.5)
    clock.advance(0.5)
    assert clock.monotonic() == 2.0
    assert clock.sleeps == [1.5]


def test_system_clock_is_monotonic():
    clock = SystemClock()
    assert clock.monotonic() <= clock.monotonic()
    assert "T" in clock.now_iso()


# --- test_errors.py --------------------------------------------------------

def test_error_codes_and_status():
    assert ValidationError("bad").http_status == 400
    assert PolicyViolation("no").to_dict()["code"] == "policy_violation"


def test_stage_error_carries_stage_and_retryable():
    err = StageError("score", "slow", retryable=True)
    assert err.stage == "score" and err.retryable


def test_circuit_open_is_not_retryable():
    err = CircuitOpenError("score")
    assert isinstance(err, StageError)
    assert err.retryable is False


# --- test_ids.py -----------------------------------------------------------

def test_new_id_prefix_and_uniqueness():
    a, b = new_id("run"), new_id("run")
    assert a.startswith("run_") and a != b


def test_stable_hash_is_order_insensitive_for_dict_keys():
    assert stable_hash({"a": 1, "b": 2}) == stable_hash({"b": 2, "a": 1})
    assert stable_hash({"a": 1}) != stable_hash({"a": 2})


# --- test_result.py --------------------------------------------------------

def test_ok_map_and_bind():
    assert Ok(2).map(lambda v: v * 3).unwrap() == 6
    assert Ok(2).bind(lambda v: Ok(v + 1)).unwrap() == 3


def test_err_short_circuits():
    err = Err("boom")
    assert err.map(lambda v: v * 3) is err
    assert err.unwrap_or(7) == 7
    with pytest.raises(RuntimeError):
        err.unwrap()


def test_collect_returns_first_error():
    assert collect([Ok(1), Ok(2)]).unwrap() == [1, 2]
    assert collect([Ok(1), Err("x"), Err("y")]).error == "x"


# --- test_specification.py -------------------------------------------------

even = Specification(lambda n: n % 2 == 0, "even")
positive = Specification(lambda n: n > 0, "positive")


def test_composition():
    assert (even & positive).is_satisfied_by(4)
    assert not (even & positive).is_satisfied_by(-4)
    assert (even | positive).is_satisfied_by(3)
    assert (~even).is_satisfied_by(3)


def test_constants():
    assert ALWAYS.is_satisfied_by(None) and not NEVER.is_satisfied_by(None)


# --- test_text.py ----------------------------------------------------------

def test_tokenize_drops_stopwords():
    assert tokenize("The Policy and the Retrieval") == ["policy", "retrieval"]
    assert "the" in tokenize("the policy", drop_stopwords=False)


def test_normalize_and_snippet():
    assert normalize("  a   b \n c ") == "a b c"
    assert snippet("x" * 300, 10).endswith("…")
    assert len(snippet("x" * 300, 10)) == 10


def test_estimate_tokens_is_positive():
    assert estimate_tokens("") == 1
    assert estimate_tokens("abcdefgh") == 3
