# ADR 0001: Adopt hexagonal architecture

- Status: accepted

## Context

The core must stay testable without infrastructure and adapters must be swappable.

## Decision

Ports in `ports/`, adapters in `adapters/`, a single composition root.

## Consequences

More indirection; every new dependency needs a port.
