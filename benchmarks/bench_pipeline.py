"""Latency and throughput for synthetic requests at several candidate counts."""

import random
import statistics
import time

from answer_or_abstain_rag.application.commands import RunPipeline
from answer_or_abstain_rag.container import build_container

WORDS = "policy retrieval evidence ranking budget tenant answer cache audit approval".split()


def make_request(rng, n):
    return {
        "query": " ".join(rng.sample(WORDS, 3)),
        "principal": {"roles": ["analyst"], "groups": ["eng"]},
        "candidates": [
            {"doc_id": f"d{i}", "text": " ".join(rng.choices(WORDS, k=20)), "score": rng.random(), "classification": "internal"}
            for i in range(n)
        ],
    }


def main():
    rng = random.Random(7)
    container = build_container()
    print(f"{'candidates':>10} {'p50 ms':>8} {'p95 ms':>8} {'runs/s':>8}")
    for n in (10, 50, 100, 200):
        timings = []
        for _ in range(100):
            body = make_request(rng, n)
            start = time.perf_counter()
            container.bus.handle(RunPipeline(request=body))
            timings.append((time.perf_counter() - start) * 1000)
        timings.sort()
        p95 = timings[int(len(timings) * 0.95) - 1]
        print(f"{n:>10} {statistics.median(timings):>8.2f} {p95:>8.2f} {1000 / statistics.mean(timings):>8.1f}")


if __name__ == "__main__":
    main()
