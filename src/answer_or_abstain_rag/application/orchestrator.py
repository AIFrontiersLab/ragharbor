"""The orchestrator executes stages with tracing, retries, circuit breakers, and checkpoints.

Failure semantics
-----------------
* Non-critical stage fails  -> run continues, ``degraded`` is set, a fallback stage can repair ordering.
* Critical stage fails      -> run stops. A failing policy stage fails *closed* (abstain), never open.
* Expected outcomes (abstain, approval required) are not failures; they are terminal states.
"""

from __future__ import annotations

from answer_or_abstain_rag.domain import events
from answer_or_abstain_rag.domain.models import Outcome, PipelineContext, Request, StageEvent
from answer_or_abstain_rag.kernel.clock import Clock
from answer_or_abstain_rag.kernel.errors import StageError
from answer_or_abstain_rag.kernel.ids import new_id
from answer_or_abstain_rag.observability.logging import get_logger
from answer_or_abstain_rag.resilience.circuit_breaker import CircuitBreaker
from answer_or_abstain_rag.resilience.retry import RetryPolicy
from answer_or_abstain_rag.resilience.timeout import Deadline
from answer_or_abstain_rag.stages.base import Stage
from answer_or_abstain_rag.workflows.state_machine import RunState, RunStateMachine

log = get_logger("orchestrator")


class Orchestrator:
    def __init__(
        self,
        stages: list[Stage],
        *,
        clock: Clock,
        tracer,
        metrics,
        event_bus,
        hooks,
        checkpoints,
        cache,
        breakers: dict[str, CircuitBreaker],
        retry: RetryPolicy,
        bulkhead,
        stage_timeout_ms: float,
    ) -> None:
        self.stages = stages
        self.clock = clock
        self.tracer = tracer
        self.metrics = metrics
        self.event_bus = event_bus
        self.hooks = hooks
        self.checkpoints = checkpoints
        self.cache = cache
        self.breakers = breakers
        self.retry = retry
        self.bulkhead = bulkhead
        self.stage_timeout_ms = stage_timeout_ms

    def execute(self, request: Request, *, run_id: str | None = None) -> Outcome:
        run_id = run_id or new_id("run")
        machine = RunStateMachine()
        ctx = PipelineContext(run_id=run_id, request=request)
        with self.bulkhead.slot():
            machine.transition(RunState.RUNNING)
            self._publish(events.RUN_STARTED, run_id, tenant=request.tenant)
            with self.tracer.span("run", run_id=run_id):
                failed = self._run_stages(ctx)
        status = self._finalise(ctx, machine, failed)
        outcome = Outcome(
            run_id=run_id,
            status=status,
            query=request.query,
            answer=ctx.answer,
            abstain_reason=ctx.abstain_reason,
            degraded=ctx.degraded,
            cache_hit=ctx.cache_hit,
            events=ctx.events,
            decisions=ctx.decisions,
            errors=ctx.errors,
            tokens_used=ctx.tokens_used,
        )
        self.hooks.fire("on_complete", outcome=outcome)
        self.metrics.inc("pipeline_runs_total", status=status)
        return outcome

    # ------------------------------------------------------------------ internals

    def _run_stages(self, ctx: PipelineContext) -> bool:
        fail_stages = set(ctx.request.options.get("fail_stages") or [])
        for stage in self.stages:
            if ctx.halted:
                ctx.events.append(StageEvent(stage=stage.name, status="skipped", detail={"reason": "halted"}))
                continue
            self.hooks.fire("before_stage", stage=stage, ctx=ctx)
            start = self.clock.monotonic()
            deadline = Deadline(self.stage_timeout_ms, clock=self.clock)
            status = "ok"
            detail: dict = {"role": stage.role}
            try:
                with self.tracer.span(f"stage:{stage.name}", role=stage.role):
                    self._invoke(stage, ctx, inject_failure=stage.name in fail_stages)
                if deadline.expired():
                    detail["deadline_exceeded_ms"] = round(deadline.elapsed_ms(), 3)
                    self.metrics.inc("stage_deadline_exceeded_total", stage=stage.name)
            except StageError as exc:
                status = self._handle_failure(stage, ctx, exc)
                detail["error"] = exc.code
                self.hooks.fire("on_error", stage=stage, ctx=ctx, error=exc)
            duration = round((self.clock.monotonic() - start) * 1000.0, 3)
            ctx.events.append(StageEvent(stage=stage.name, status=status, duration_ms=duration, detail=detail))
            self.metrics.observe("stage_duration_ms", duration, stage=stage.name)
            self.metrics.inc("stage_executions_total", stage=stage.name, status=status)
            self.checkpoints.save(ctx.run_id, stage.name, {"status": status, "candidates": len(ctx.candidates)})
            self._flush_pending_events(ctx)
            self.hooks.fire("after_stage", stage=stage, ctx=ctx, status=status)
            if status == "failed":
                return True
        return False

    def _invoke(self, stage: Stage, ctx: PipelineContext, *, inject_failure: bool) -> None:
        breaker = self.breakers.get(stage.name)

        def attempt() -> None:
            if inject_failure:
                raise StageError(stage.name, "injected failure", retryable=False)
            stage.process(ctx)

        def guarded() -> None:
            try:
                self.retry.call(attempt)
            except StageError:
                raise
            except Exception as exc:  # defects become non-retryable stage errors
                raise StageError(stage.name, f"{type(exc).__name__}: {exc}", retryable=False) from exc

        if breaker is None:
            guarded()
        else:
            breaker.call(guarded)

    def _handle_failure(self, stage: Stage, ctx: PipelineContext, exc: StageError) -> str:
        ctx.errors.append({"stage": stage.name, "code": exc.code, "message": exc.message})
        log.warning("stage failed", fields={"run_id": ctx.run_id, "stage": stage.name, "code": exc.code})
        if not stage.critical:
            ctx.degraded = True
            self._publish(events.STAGE_DEGRADED, ctx.run_id, stage=stage.name)
            return "degraded"
        if stage.role == "policy":
            ctx.candidates = []
            ctx.abstain("policy_unavailable")
            return "failed_closed"
        ctx.abstain(f"stage_failure:{stage.name}")
        return "failed"

    def _finalise(self, ctx: PipelineContext, machine: RunStateMachine, failed: bool) -> str:
        if failed:
            machine.transition(RunState.FAILED)
            self._publish(events.RUN_FAILED, ctx.run_id, reason=ctx.abstain_reason)
            return machine.state.value
        if ctx.abstain_reason == "approval_required":
            machine.transition(RunState.AWAITING_APPROVAL)
            self._publish(events.APPROVAL_REQUESTED, ctx.run_id)
            return machine.state.value
        if ctx.answer is None:
            if not ctx.abstain_reason:
                ctx.abstain_reason = "no_answer_produced"
            machine.transition(RunState.ABSTAINED)
            self._publish(events.RUN_ABSTAINED, ctx.run_id, reason=ctx.abstain_reason)
            return machine.state.value
        machine.transition(RunState.COMPLETED)
        self._store_ranking(ctx)
        self._publish(events.RUN_COMPLETED, ctx.run_id, citations=len(ctx.answer.citations))
        return machine.state.value

    def _store_ranking(self, ctx: PipelineContext) -> None:
        key = ctx.metadata.get("cache_key")
        if key and self.cache is not None and not ctx.degraded and not ctx.cache_hit:
            self.cache.put(key, [(c.doc_id, c.score) for c in ctx.candidates])

    def _flush_pending_events(self, ctx: PipelineContext) -> None:
        for name, payload in ctx.metadata.pop("pending_events", []):
            self._publish(name, ctx.run_id, **payload)

    def _publish(self, name: str, run_id: str, **payload) -> None:
        self.event_bus.publish(events.event(name, run_id, at=self.clock.now_iso(), **payload))
