# Performance

The reference pipeline is CPU-bound and linear in the number of candidates per stage.
`benchmarks/bench_pipeline.py` reports p50/p95 latency and throughput for configurable
candidate counts. Main levers: `pipeline.max_candidates`, cache capacity and TTL, `top_k`,
and replacing the lexical scorer with a batched model server.
