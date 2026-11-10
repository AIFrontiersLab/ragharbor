# ADR 0003: Policy failures fail closed

- Status: accepted

## Context

Releasing unauthorised content is worse than abstaining.

## Decision

The policy role is critical; on failure all candidates are dropped and the run abstains.

## Consequences

Availability drops during policy outages.
