# ADR 0007: Explicit run state machine

- Status: accepted

## Context

Approval pauses and resumptions need well-defined states.

## Decision

`RunStateMachine` with a transition table; illegal moves raise.

## Consequences

Slight ceremony for simple runs.
