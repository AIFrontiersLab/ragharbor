"""Call a running server: python -m <pkg> serve, then run this file."""

import json
import urllib.request
from pathlib import Path

body = (Path(__file__).parent / "requests" / "governed_query.json").read_bytes()
req = urllib.request.Request("http://127.0.0.1:8080/v1/runs", data=body, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    print(json.dumps(json.load(resp), indent=2))
