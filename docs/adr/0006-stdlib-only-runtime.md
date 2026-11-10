# ADR 0006: Zero runtime dependencies

- Status: accepted

## Context

Reference code should be readable and installable anywhere.

## Decision

WSGI via `wsgiref`, TOML via `tomllib`, dataclasses for models.

## Consequences

Some conveniences of frameworks are re-implemented minimally.
