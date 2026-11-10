#!/usr/bin/env bash
set -euo pipefail
BASE=${BASE:-http://127.0.0.1:8080}
curl -fsS "$BASE/healthz"
curl -fsS "$BASE/readyz"
curl -fsS -X POST -H 'Content-Type: application/json' --data @examples/requests/governed_query.json "$BASE/v1/runs" | head -c 400
echo
