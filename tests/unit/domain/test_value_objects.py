import pytest

from answer_or_abstain_rag.domain.value_objects import Clearance, Score, TokenBudget
from answer_or_abstain_rag.kernel.errors import ValidationError


def test_clearance_ordering_and_parse():
    assert Clearance.parse("restricted") > Clearance.parse("internal")
    assert Clearance.parse(Clearance.PUBLIC) is Clearance.PUBLIC
    with pytest.raises(ValidationError):
        Clearance.parse("top-secret")


def test_score_clamp_and_nan_guard():
    assert Score(1.7).clamp().value == 1.0
    with pytest.raises(ValidationError):
        Score(float("nan"))


def test_token_budget_spending():
    budget = TokenBudget(10).spend(4)
    assert budget.remaining == 6
    assert budget.can_afford(6) and not budget.can_afford(7)
    with pytest.raises(ValidationError):
        TokenBudget(-1)
