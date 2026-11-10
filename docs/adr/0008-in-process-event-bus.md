# ADR 0008: In-process event bus behind a port

- Status: accepted

## Context

Events are useful for audit and integration, but a broker is not needed for the reference.

## Decision

Synchronous bus with dead-letter capture.

## Consequences

Not durable; bridge to a broker in production.
