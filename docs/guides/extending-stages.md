# Extending stages

1. Subclass `answer_or_abstain_rag.stages.base.Stage` (or an existing role class) and implement `process(ctx)`.
2. Register a factory: `registry.register("my_stage", "score", lambda s: MyStage("my_stage", s))`.
3. Add the name to `pipeline.stages` in a profile.
4. Add a test under `tests/unit/` and confirm `tests/contract/test_stage_contract.py` passes.

Rules: never introduce duplicate ids; raise `StageError` for recoverable faults; record
decisions with `ctx.decide(...)`; never do I/O except through `services`.
