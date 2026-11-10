# ADR 0004: Degrade, do not fail, on non-critical stage errors

- Status: accepted

## Context

Optional enrichments should not take the service down.

## Decision

Non-critical stage errors set `degraded`; a fallback stage restores prior order.

## Consequences

Degraded answers may be lower quality; surfaced via the `degraded` flag and metrics.
