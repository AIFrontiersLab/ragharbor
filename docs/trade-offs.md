# Trade-offs

## Built-in vs learned scoring

The lexical reference scorer is deterministic and dependency-free; learned scorers improve relevance at the cost of latency, cost, and reproducibility.

## Degrade vs fail

Non-critical stages degrade to protect availability; policy and answer assembly fail to protect correctness.
