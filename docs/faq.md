# FAQ

**Why no web framework?** Zero runtime dependencies keep the reference readable and portable. Any WSGI server can host `HttpApp`.

**Can I use a neural reranker?** Yes. Implement `RelevanceScorer.score(query, candidate) -> float` and pass `scorer=` to `build_container`.

**Why does a run abstain instead of answering?** Read `abstain_reason` and `decisions`. Common reasons: `insufficient_evidence`, `budget_exhausted`, `approval_required`, `policy_unavailable`.

**How do I change stage order?** Set `pipeline.stages` in a profile or `ANSWER_OR_ABSTAIN_RAG_PIPELINE__STAGES=a,b,c`.
