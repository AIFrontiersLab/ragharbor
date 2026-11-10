#!/usr/bin/env bash
set -euo pipefail
export ANSWER_OR_ABSTAIN_RAG_CONFIG=${ANSWER_OR_ABSTAIN_RAG_CONFIG:-config/development.toml}
PYTHONPATH=src exec python -m answer_or_abstain_rag serve "$@"
