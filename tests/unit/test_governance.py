import pytest

from answer_or_abstain_rag.domain.models import Candidate, Principal, Request
from answer_or_abstain_rag.governance.approvals import ApprovalService
from answer_or_abstain_rag.governance.budgets import BudgetGuard
from answer_or_abstain_rag.governance.pii import detect
from answer_or_abstain_rag.governance.policy_engine import Decision, PolicyEngine
from answer_or_abstain_rag.governance.rbac import Permission, authorize, permissions_for
from answer_or_abstain_rag.governance.redaction import Redactor
from answer_or_abstain_rag.kernel.errors import NotFound, PolicyViolation

# --- test_approvals.py -----------------------------------------------------

def test_request_approve_and_token():
    svc = ApprovalService(secret="s")
    svc.request("r1", risk=0.9, reason="restricted")
    assert [t["run_id"] for t in svc.pending()] == ["r1"]
    token = svc.approve("r1", "boss")
    assert svc.is_approved("r1") and token == svc.token_for("r1")
    assert svc.pending() == []


def test_approving_unknown_run_fails():
    with pytest.raises(NotFound):
        ApprovalService().approve("nope", "x")


def test_tokens_depend_on_secret():
    assert ApprovalService("a").token_for("r") != ApprovalService("b").token_for("r")


# --- test_budgets.py -------------------------------------------------------

def test_default_and_hard_limit():
    guard = BudgetGuard(default_tokens=100, hard_limit_tokens=500)
    assert guard.for_request(Request.from_dict({"query": "q"})).limit == 100
    assert guard.for_request(Request.from_dict({"query": "q", "budget_tokens": 9999})).limit == 500


# --- test_pii.py -----------------------------------------------------------

def test_detects_common_identifiers():
    kinds = {k for k, _ in detect("ssn 123-45-6789, mail a@b.io, card 4111 1111 1111 1111")}
    assert {"ssn", "email", "credit_card"} <= kinds


def test_clean_text_has_no_hits():
    assert detect("policy enforcement for retrieval") == []


# --- test_policy_engine.py -------------------------------------------------

ROLES = {"reader": "internal", "admin": "restricted"}


def test_deny_overrides_in_rule_order():
    engine = PolicyEngine(ROLES, "public")
    cand = Candidate("d", classification="restricted", metadata={"tenant": "other"})
    assert engine.evaluate(Principal(roles=("admin",), tenant="acme"), cand).reason == "tenant_mismatch"


def test_extra_rules_are_applied():
    deny_drafts = lambda p, c: Decision(False, "draft") if c.metadata.get("draft") else None  # noqa: E731
    engine = PolicyEngine(ROLES, "public", extra_rules=[deny_drafts])
    assert engine.evaluate(Principal(roles=("admin",)), Candidate("d", metadata={"draft": True})).reason == "draft"
    assert engine.evaluate(Principal(roles=("admin",)), Candidate("d")).allowed


# --- test_rbac.py ----------------------------------------------------------

def test_admin_has_everything_guest_has_little():
    assert permissions_for(Principal(roles=("admin",))) == frozenset(Permission)
    assert permissions_for(Principal(roles=("guest",))) == {Permission.RUN_PIPELINE}


def test_authorize_raises_with_details():
    with pytest.raises(PolicyViolation) as info:
        authorize(Principal(subject="g", roles=("guest",)), Permission.APPROVE_RUN)
    assert info.value.details["permission"] == "run:approve"


# --- test_redaction.py -----------------------------------------------------

def test_redaction_replaces_and_counts():
    text, hits = Redactor().redact("contact a@b.io and c@d.io")
    assert text == "contact [EMAIL] and [EMAIL]"
    assert hits == {"email": 2}
