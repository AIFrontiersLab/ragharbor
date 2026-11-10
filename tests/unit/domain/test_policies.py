from answer_or_abstain_rag.domain.models import Candidate, Principal
from answer_or_abstain_rag.domain.policies import acl_allows, clearance_allows, principal_clearance, tenant_allows
from answer_or_abstain_rag.domain.value_objects import Clearance

ROLES = {"reader": "internal", "admin": "restricted"}


def test_principal_clearance_takes_highest_role():
    p = Principal(roles=("reader", "admin"))
    assert principal_clearance(p, ROLES, "public") is Clearance.RESTRICTED
    assert principal_clearance(Principal(roles=("unknown",)), ROLES, "public") is Clearance.PUBLIC


def test_clearance_and_acl_rules():
    secret = Candidate("d", classification="confidential", acl=("security",))
    assert not clearance_allows(Clearance.INTERNAL, secret)
    assert clearance_allows(Clearance.RESTRICTED, secret)
    assert not acl_allows(Principal(groups=("eng",)), secret)
    assert acl_allows(Principal(groups=("security",)), secret)
    assert acl_allows(Principal(), Candidate("open"))


def test_tenant_rule():
    owned = Candidate("d", metadata={"tenant": "acme"})
    assert tenant_allows(Principal(tenant="acme"), owned)
    assert not tenant_allows(Principal(tenant="globex"), owned)
