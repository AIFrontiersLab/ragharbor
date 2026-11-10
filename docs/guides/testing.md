# Testing

- `FakeClock` makes breakers, rate limits, TTLs, and deadlines deterministic.
- `build_container(settings, clock=..., corpus=..., scorer=...)` swaps any dependency.
- `options.fail_stages` injects failures for degradation tests.
- Property tests are seeded; a failing seed reproduces exactly.
