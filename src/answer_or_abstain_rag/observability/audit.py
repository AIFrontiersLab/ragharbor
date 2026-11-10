"""Audit trail helpers: build tamper-evident chains over audit records."""

from __future__ import annotations

from answer_or_abstain_rag.kernel.ids import stable_hash


def chain(records: list[dict]) -> list[dict]:
    """Return records annotated with a hash chain so deletions or edits are detectable."""
    previous = "genesis"
    out = []
    for record in records:
        digest = stable_hash({"prev": previous, "record": record}, length=32)
        out.append({**record, "prev_hash": previous, "hash": digest})
        previous = digest
    return out


def verify_chain(chained: list[dict]) -> bool:
    previous = "genesis"
    for item in chained:
        body = {k: v for k, v in item.items() if k not in {"prev_hash", "hash"}}
        if item.get("prev_hash") != previous:
            return False
        if stable_hash({"prev": previous, "record": body}, length=32) != item.get("hash"):
            return False
        previous = item["hash"]
    return True
