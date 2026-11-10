# ADR 0002: Model the pipeline as registered stage strategies

- Status: accepted

## Context

The pipeline topology changes per concept and per deployment.

## Decision

Stages implement one `process(ctx)` method and are created by name from a registry; order is configuration.

## Consequences

Ordering mistakes are possible, mitigated by role-sorted defaults and catalog tests.
