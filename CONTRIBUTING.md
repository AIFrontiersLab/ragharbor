# Contributing

1. Open an issue describing the change.
2. Add or update an ADR for structural changes.
3. Keep the dependency rule: nothing in `kernel`, `domain`, or `stages` may import an adapter.
4. `make lint test` must pass.
5. New stages need a unit test and must pass the stage contract test.
