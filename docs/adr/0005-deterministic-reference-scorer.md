# ADR 0005: Ship a deterministic reference scorer

- Status: accepted

## Context

Tests must be reproducible and the repo must run without model downloads.

## Decision

BM25-style lexical scorer behind `RelevanceScorer`.

## Consequences

Lower relevance than learned models; production swaps the adapter.
