.PHONY: install test test-fast lint bench run serve docker clean

install:
	pip install -e ".[dev]"

test:
	python -m pytest

test-fast:
	python -m pytest tests/unit

lint:
	ruff check src tests

bench:
	PYTHONPATH=src python benchmarks/bench_pipeline.py

run:
	PYTHONPATH=src python -m answer_or_abstain_rag run examples/requests/governed_query.json

serve:
	PYTHONPATH=src python -m answer_or_abstain_rag serve

docker:
	docker build -t answer-or-abstain-rag:local .

clean:
	rm -rf .pytest_cache build dist *.egg-info var
